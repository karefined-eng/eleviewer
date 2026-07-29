"""Hybrid TTS via Microsoft Edge (edge-tts) with graceful fallback to native SAPI (pyttsx3)."""

import queue
import threading
import asyncio
import os
import tempfile
import time
import ctypes
from pathlib import Path

try:
    import edge_tts
    EDGE_AVAILABLE = True
except ImportError:
    EDGE_AVAILABLE = False

try:
    import pyttsx3
    PYTTSX3_AVAILABLE = True
except ImportError:
    PYTTSX3_AVAILABLE = False

TTS_AVAILABLE = EDGE_AVAILABLE or PYTTSX3_AVAILABLE


class TtsEngine:
    """
    Hybrid Neural + Local TTS engine.
    Attempts edge-tts for high-quality voices, falls back to pyttsx3 if offline.
    """

    def __init__(self, on_error=None):
        self._on_error = on_error
        self._queue = queue.Queue()
        
        self._edge_voices = []
        self._local_voices = []
        
        self._edge_available = False
        self._local_available = False
        
        self._pyttsx3_engine = None
        
        # Temp audio file for edge-tts
        self._temp_dir = Path(tempfile.gettempdir()) / "eleviewer_tts"
        self._temp_dir.mkdir(parents=True, exist_ok=True)
        self._audio_file = self._temp_dir / "speech.mp3"
        
        if EDGE_AVAILABLE or PYTTSX3_AVAILABLE:
            try:
                self._thread = threading.Thread(target=self._worker, daemon=True)
                self._thread.start()
                self._queue.put(("init", None))
            except Exception as e:
                print(f"[TTS] Thread start failed: {e}")
        else:
            self._thread = None

    def _report_error(self, message):
        if self._on_error:
            self._on_error(message)

    def _worker(self):
        """Synchronous worker thread managing both engines."""
        while True:
            try:
                cmd, payload = self._queue.get()
                if cmd == "shutdown":
                    break
                elif cmd == "stop":
                    # Just an explicit stop handled by clearing queue and interrupting engines
                    pass
                elif cmd == "init":
                    # Initialize local pyttsx3 engine
                    if PYTTSX3_AVAILABLE:
                        try:
                            self._pyttsx3_engine = pyttsx3.init()
                            voices = self._pyttsx3_engine.getProperty("voices") or []
                            self._local_voices = [(v.id, f"[Offline] {v.name}") for v in voices]
                            self._local_available = True
                        except Exception as e:
                            self._local_available = False
                            print(f"[TTS] Local Pyttsx3 Init Error: {e}")

                    # Fetch online edge-tts voices (cached)
                    if EDGE_AVAILABLE and not self._edge_voices:
                        try:
                            all_voices = self._run_async(self._fetch_edge_voices())
                            voices = sorted(all_voices, key=lambda x: x["FriendlyName"])
                            self._edge_voices = [(v["ShortName"], f"[Online] {v['FriendlyName']} ({v['Locale']})") for v in voices]
                            self._edge_available = True
                        except Exception as e:
                            self._edge_available = False
                            print(f"[TTS] Online Edge-TTS Init Error (likely offline): {e}")

                elif cmd == "speak":
                    text, voice_id = payload
                    
                    # Stop any current playback (in case it leaked)
                    self.stop()
                    
                    use_edge = False
                    
                    if not voice_id:
                        # Default preference: Online Aria, fallback to first local
                        if self._edge_available:
                            voice_id = "en-US-AriaNeural"
                            use_edge = True
                        elif self._local_available and self._local_voices:
                            voice_id = self._local_voices[0][0]
                    else:
                        # Check which list the voice_id belongs to
                        is_local = any(v[0] == voice_id for v in self._local_voices)
                        use_edge = not is_local and self._edge_available

                    # Execute playback
                    if use_edge:
                        try:
                            self._run_async(self._speak_edge(text, voice_id))
                        except Exception as e:
                            print(f"[TTS] Online generation failed ({e}), falling back to offline.")
                            if self._local_available:
                                self._speak_local(text, None)
                            else:
                                self._report_error("Online TTS failed and no offline voices are available.")
                    else:
                        if self._local_available:
                            self._speak_local(text, voice_id)

            except Exception as e:
                self._report_error(str(e))

    def _run_async(self, coro):
        """Safe wrapper to run asyncio loop handling edge cases."""
        try:
            return asyncio.run(coro)
        except RuntimeError:
            loop = asyncio.get_event_loop()
            return loop.run_until_complete(coro)

    async def _fetch_edge_voices(self):
        # 5-second timeout so we don't stall init forever if network is a blackhole
        return await asyncio.wait_for(edge_tts.VoicesManager.create(), timeout=5.0)

    async def _speak_edge(self, text, voice_id):
        """Generate online audio and play via native Windows API synchronously."""
        communicate = edge_tts.Communicate(text, voice_id)
        
        # Download audio with timeout to trigger fallback if connection drops
        await asyncio.wait_for(communicate.save(str(self._audio_file)), timeout=10.0)
        
        # Play using native Windows mciSendString (Zero dependencies, plays MP3 natively)
        if os.name == 'nt':
            path_str = str(self._audio_file)
            ctypes.windll.winmm.mciSendStringW('close edge_media', None, 0, None)
            ctypes.windll.winmm.mciSendStringW(f'open "{path_str}" alias edge_media', None, 0, None)
            # wait keyword blocks the thread until playback finishes (interruptible by close)
            ctypes.windll.winmm.mciSendStringW('play edge_media wait', None, 0, None)
            ctypes.windll.winmm.mciSendStringW('close edge_media', None, 0, None)

    def _speak_local(self, text, voice_id):
        """Synchronous local playback using pyttsx3."""
        if not self._pyttsx3_engine:
            return
        
        if voice_id:
            try:
                self._pyttsx3_engine.setProperty("voice", voice_id)
            except Exception:
                pass
        
        self._pyttsx3_engine.say(text)
        # This blocks until finished or interrupted by self._pyttsx3_engine.stop()
        self._pyttsx3_engine.runAndWait()

    def list_voices(self):
        # Return merged list
        # We try to wait a tiny bit if init is currently running
        for _ in range(20):
            if self._edge_voices or self._local_voices:
                break
            time.sleep(0.1)
            
        return self._edge_voices + self._local_voices

    def speak(self, text, voice_id=None):
        if not text or not text.strip():
            return
        if EDGE_AVAILABLE or PYTTSX3_AVAILABLE:
            self._queue.put(("speak", (text, voice_id)))

    def stop(self):
        """Force stops all engines from any thread."""
        if not EDGE_AVAILABLE and not PYTTSX3_AVAILABLE:
            return

        # 1. Clear queue
        while not self._queue.empty():
            try:
                self._queue.get_nowait()
            except queue.Empty:
                break
                
        # 2. Interrupt Edge TTS playback (native Windows MCI)
        if os.name == 'nt':
            try:
                ctypes.windll.winmm.mciSendStringW('stop edge_media', None, 0, None)
                ctypes.windll.winmm.mciSendStringW('close edge_media', None, 0, None)
            except Exception:
                pass

        # 3. Interrupt Pyttsx3
        if getattr(self, "_pyttsx3_engine", None):
            try:
                self._pyttsx3_engine.stop()
            except Exception:
                pass

        # Also push a stop command to wake up the queue if idle
        self._queue.put(("stop", None))


TTSEngine = TtsEngine
PdfTts = TtsEngine
