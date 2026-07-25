"""Windows native TTS via SAPI (pyttsx3) with a dedicated worker thread."""

import queue
import threading

try:
    import pyttsx3
    TTS_AVAILABLE = True
except ImportError:
    TTS_AVAILABLE = False


# FIX: safe init with try/except — TTS degrades gracefully if unavailable
class TtsEngine:

    def __init__(self, on_error=None):
        self._on_error = on_error
        self._queue = queue.Queue()
        self._voices = []
        self._available = False
        if TTS_AVAILABLE:
            try:
                self._thread = threading.Thread(target=self._worker, daemon=True)
                self._thread.start()
                self._queue.put(("init", None))
            except Exception as e:
                self._available = False
                print(f"[TTS] Engine unavailable: {e}")
        else:
            self._thread = None

    def _report_error(self, message):
        if self._on_error:
            self._on_error(message)

    def _worker(self):
        engine = None
        while True:
            try:
                cmd, payload = self._queue.get()
            except Exception:
                continue

            if cmd == "shutdown":
                break

            try:
                if cmd == "init":
                    try:
                        engine = pyttsx3.init()
                        voices = engine.getProperty("voices") or []
                        self._voices = [(v.id, v.name) for v in voices]
                        self._available = True
                    except Exception as e:
                        self._available = False
                        self._report_error(str(e))

                elif cmd == "speak" and engine and self._available:
                    engine.stop()
                    text, voice_id = payload
                    if voice_id:
                        engine.setProperty("voice", voice_id)
                    engine.say(text)
                    engine.runAndWait()

                elif cmd == "stop" and engine and self._available:
                    engine.stop()

            except Exception as e:
                self._report_error(str(e))

    def list_voices(self):
        if not TTS_AVAILABLE or not self._available:
            return []
        if not self._voices and self._thread:
            self._queue.put(("init", None))
            for _ in range(20):
                if self._voices:
                    break
                threading.Event().wait(0.05)
        return list(self._voices)

    def speak(self, text, voice_id=None):
        if not text or not text.strip() or not TTS_AVAILABLE or not self._available:
            return
        self._queue.put(("speak", (text, voice_id)))

    def stop(self):
        if TTS_AVAILABLE and self._available:
            self._queue.put(("stop", None))


TTSEngine = TtsEngine  # Alias for prompt guide compatibility
PdfTts = TtsEngine     # Backward compatibility alias
