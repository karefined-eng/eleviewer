"""Hybrid TTS via Microsoft Edge (edge-tts) with graceful fallback to native SAPI (pyttsx3)."""

import asyncio
import base64
import ctypes
import os
import queue
import subprocess
import tempfile
import threading
import time
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

# Windows always has its own built-in speech, so reading aloud can always
# attempt at least the native fallback there.
TTS_AVAILABLE = EDGE_AVAILABLE or PYTTSX3_AVAILABLE or os.name == "nt"


class TtsEngine:
    """
    Hybrid Neural + Local TTS engine.
    Attempts edge-tts for high-quality voices, falls back to pyttsx3 if offline,
    and finally to Windows' own built-in speech so a broken offline engine
    never leaves the user in silence.
    """

    def __init__(self, on_error=None):
        self._on_error = on_error
        self._queue = queue.Queue()

        self._edge_voices = []
        self._local_voices = []

        self._edge_available = False
        self._local_available = False

        self._pyttsx3_engine = None
        self._native_proc = None

        # Temp audio file for edge-tts
        self._temp_dir = Path(tempfile.gettempdir()) / "eleviewer_tts"
        self._temp_dir.mkdir(parents=True, exist_ok=True)
        self._audio_file = self._temp_dir / "speech.mp3"

        if TTS_AVAILABLE:
            try:
                self._thread = threading.Thread(target=self._worker, daemon=True)
                self._thread.start()
                self._queue.put(("init", None))
            except Exception as e:
                print(f"[TTS] Thread start failed: {e}")
                self._thread = None
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
                            voices = self._initialize_local_engine()
                            self._local_voices = [(v.id, f"[Offline] {v.name}") for v in voices]
                            self._local_available = bool(self._local_voices)
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
                    is_local = False

                    if not voice_id:
                        # Default preference: best online voice, fallback to first local
                        if self._edge_available:
                            voice_id = self._default_edge_voice()
                            use_edge = True
                        elif self._local_available and self._local_voices:
                            voice_id = self._local_voices[0][0]
                            is_local = True
                    else:
                        # Check which list the voice_id belongs to
                        is_local = any(v[0] == voice_id for v in self._local_voices)
                        use_edge = not is_local and self._edge_available

                    if use_edge:
                        try:
                            self._run_async(self._speak_edge(text, voice_id))
                            continue
                        except Exception as e:
                            print(f"[TTS] Online generation failed ({e}), falling back to offline.")

                    # Offline chain: pyttsx3 first, then Windows' own built-in speech.
                    if is_local and self._local_available:
                        self._speak_local(text, voice_id)
                    elif self._local_available:
                        self._speak_local(text, None)
                    elif not self._speak_native_windows(text):
                        self._report_error(
                            "Reading aloud isn't working — no speaking voices could be started on this computer."
                        )

            except Exception as e:
                self._report_error(str(e))

    def _default_edge_voice(self):
        """Pick a sensible online voice from the ones actually available."""
        for vid, _name in self._edge_voices:
            if vid.startswith("en-US"):
                return vid
        if self._edge_voices:
            return self._edge_voices[0][0]
        return "en-US-AriaNeural"

    def _run_async(self, coro):
        """Safe wrapper to run asyncio loop handling edge cases."""
        try:
            return asyncio.run(coro)
        except RuntimeError:
            loop = asyncio.get_event_loop()
            return loop.run_until_complete(coro)

    async def _fetch_edge_voices(self):
        # 5-second timeout so we don't stall init forever if network is a blackhole
        return await asyncio.wait_for(edge_tts.list_voices(), timeout=5.0)

    async def _speak_edge(self, text, voice_id):
        """Generate online audio and play via native Windows API synchronously."""
        communicate = edge_tts.Communicate(text, voice_id)

        # Download audio with timeout to trigger fallback if connection drops
        await asyncio.wait_for(communicate.save(str(self._audio_file)), timeout=10.0)

        # Play using native Windows mciSendString (Zero dependencies, plays MP3 natively)
        if os.name == 'nt':
            path_str = str(self._audio_file)
            self._mci_send('close edge_media')
            if self._mci_send(f'open "{path_str}" alias edge_media') != 0:
                raise RuntimeError("Windows could not open the generated audio")
            try:
                # wait keyword blocks the thread until playback finishes (interruptible by close)
                self._mci_send('play edge_media wait')
            finally:
                self._mci_send('close edge_media')

    @staticmethod
    def _mci_send(command):
        """Send a Windows media command; returns 0 on success, error code otherwise."""
        try:
            return int(ctypes.windll.winmm.mciSendStringW(command, None, 0, None))
        except Exception:
            return -1

    def _speak_local(self, text, voice_id):
        """Synchronous local playback using pyttsx3, with Windows' built-in speech as backup."""
        for attempt in range(2):
            engine = self._pyttsx3_engine
            if engine is None:
                try:
                    self._initialize_local_engine()
                except Exception as reset_error:
                    self._report_error(f"Offline reading aloud could not start: {reset_error}")
                    return
                engine = self._pyttsx3_engine

            try:
                if voice_id:
                    engine.setProperty("voice", voice_id)
                engine.say(text)
                engine.runAndWait()
                return
            except Exception as error:
                if attempt:
                    # pyttsx3 failed twice — try Windows' own speech before giving up
                    if not self._speak_native_windows(text):
                        self._report_error(f"Offline reading aloud failed: {error}")
                    return
                try:
                    self._initialize_local_engine()
                except Exception as reset_error:
                    self._report_error(f"Offline reading aloud could not restart: {reset_error}")
                    return

    def _speak_native_windows(self, text):
        """Last-resort playback through Windows' own built-in speech.

        Runs in a separate helper process, so it keeps working even when the
        offline voice engine is broken inside a packaged build.
        """
        if os.name != "nt":
            return False
        text = (text or "").strip()
        if not text:
            return False
        try:
            # The text travels via a temp file and the path via base64, so
            # quotes, newlines, and unusual characters can't break the helper.
            text_file = self._temp_dir / "native_speech.txt"
            text_file.write_text(text, encoding="utf-8")
            encoded_path = base64.b64encode(str(text_file).encode("utf-8")).decode("ascii")
            script = (
                "Add-Type -AssemblyName System.Speech;"
                "$s = New-Object System.Speech.Synthesis.SpeechSynthesizer;"
                "$p = [Text.Encoding]::UTF8.GetString([Convert]::FromBase64String('%s'));"
                "$s.Speak([IO.File]::ReadAllText($p))" % encoded_path
            )
            encoded_command = base64.b64encode(script.encode("utf-16-le")).decode("ascii")
            self._native_proc = subprocess.Popen(
                ["powershell", "-NoProfile", "-EncodedCommand", encoded_command],
                creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            self._native_proc.wait()
            return True
        except Exception as e:
            print(f"[TTS] Native Windows speech failed: {e}")
            return False
        finally:
            self._native_proc = None

    def _initialize_local_engine(self):
        """Create a fresh local engine after a stop/voice-switch failure."""
        if not PYTTSX3_AVAILABLE:
            return []
        self._pyttsx3_engine = pyttsx3.init()
        return self._pyttsx3_engine.getProperty("voices") or []

    def list_voices(self):
        # Return merged list
        # We try to wait a tiny bit if init is currently running
        for _ in range(20):
            if self._edge_voices or self._local_voices:
                break
            time.sleep(0.1)

        voices = self._edge_voices + self._local_voices
        if not voices and os.name == "nt":
            # Something is always better than an empty dropdown: Windows'
            # built-in voice still works when the richer engines are missing.
            voices = [(None, "[Offline] Windows built-in voice")]
        return voices

    def speak(self, text, voice_id=None):
        from auditory_cleaner import clean_for_speech
        text = clean_for_speech(text)
        if not text or not text.strip():
            return
        if TTS_AVAILABLE:
            self._queue.put(("speak", (text, voice_id)))

    def stop(self):
        """Force stops all engines from any thread."""
        if not TTS_AVAILABLE:
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

        # 4. Interrupt the native Windows speech helper
        proc = getattr(self, "_native_proc", None)
        if proc is not None:
            try:
                proc.terminate()
            except Exception:
                pass

        # Also push a stop command to wake up the queue if idle
        self._queue.put(("stop", None))

    def shutdown(self, timeout=8.0):
        """Stop playback and join the worker before the owning window is destroyed."""
        thread = getattr(self, "_thread", None)
        if thread is None:
            return
        self.stop()
        self._queue.put(("shutdown", None))
        if thread.is_alive():
            thread.join(timeout)
        if not thread.is_alive():
            self._thread = None


TTSEngine = TtsEngine
PdfTts = TtsEngine
