"""Windows native TTS via SAPI (pyttsx3) with a dedicated worker thread."""

import queue
import threading

try:
    import pyttsx3
    TTS_AVAILABLE = True
except ImportError:
    TTS_AVAILABLE = False


class TtsEngine:

    def __init__(self, on_error=None):
        self._on_error = on_error
        self._queue = queue.Queue()
        self._voices = []
        if TTS_AVAILABLE:
            self._thread = threading.Thread(target=self._worker, daemon=True)
            self._thread.start()
            self._queue.put(("init", None))
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
                    engine = pyttsx3.init()
                    voices = engine.getProperty("voices") or []
                    self._voices = [(v.id, v.name) for v in voices]

                elif cmd == "speak" and engine:
                    engine.stop()
                    text, voice_id = payload
                    if voice_id:
                        engine.setProperty("voice", voice_id)
                    engine.say(text)
                    engine.runAndWait()

                elif cmd == "stop" and engine:
                    engine.stop()

            except Exception as e:
                self._report_error(str(e))

    def list_voices(self):
        if not TTS_AVAILABLE:
            return []
        if not self._voices and self._thread:
            self._queue.put(("init", None))
            for _ in range(20):
                if self._voices:
                    break
                threading.Event().wait(0.05)
        return list(self._voices)

    def speak(self, text, voice_id=None):
        if not text or not text.strip() or not TTS_AVAILABLE:
            return
        self._queue.put(("speak", (text, voice_id)))

    def stop(self):
        if TTS_AVAILABLE:
            self._queue.put(("stop", None))

PdfTts = TtsEngine  # Backward compatibility alias
