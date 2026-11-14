from tts_engine import TtsEngine


def test_local_engine_initialization_failure_uses_native_windows_fallback():
    engine = TtsEngine.__new__(TtsEngine)
    spoken = []
    errors = []
    engine._pyttsx3_engine = None
    engine._on_error = errors.append
    engine._initialize_local_engine = lambda: (_ for _ in ()).throw(RuntimeError("SAPI unavailable"))
    engine._speak_native_windows = lambda text: spoken.append(text) or True

    engine._speak_local("Read this page", None)

    assert spoken == ["Read this page"]
    assert errors == []


def test_local_engine_restart_failure_uses_native_windows_fallback():
    class BrokenEngine:
        def setProperty(self, _name, _value):
            pass

        def say(self, _text):
            raise RuntimeError("voice failed")

        def runAndWait(self):
            raise RuntimeError("voice failed")

    engine = TtsEngine.__new__(TtsEngine)
    spoken = []
    errors = []
    engine._pyttsx3_engine = BrokenEngine()
    engine._on_error = errors.append
    engine._initialize_local_engine = lambda: (_ for _ in ()).throw(RuntimeError("SAPI unavailable"))
    engine._speak_native_windows = lambda text: spoken.append(text) or True

    engine._speak_local("Read this page", "voice-id")

    assert spoken == ["Read this page"]
    assert errors == []
