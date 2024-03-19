import os
import queue

from google.cloud import speech
import threading

import pyaudio

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'credentials\skilful-bloom-412006-dbb611c1b6da.json'

# Audio recording parameters
RATE = 16000
CHUNK = int(RATE / 10)  # 100ms

class MicrophoneStream:

    def __init__(self: object, rate: int = RATE, chunk: int = CHUNK) -> None:
        self._rate = rate
        self._chunk = chunk

        self._buff = queue.Queue()
        self.closed = True

    def __enter__(self: object) -> object:
        self._audio_interface = pyaudio.PyAudio()
        self._audio_stream = self._audio_interface.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=self._rate,
            input=True,
            frames_per_buffer=self._chunk,
            
            stream_callback=self._fill_buffer,
        )

        self.closed = False

        return self

    def __exit__(
        self: object,
        type: object,
        value: object,
        traceback: object,
    ) -> None:
        self._audio_stream.stop_stream()
        self._audio_stream.close()
        self.closed = True
        
        self._buff.put(None)
        self._audio_interface.terminate()

    def _fill_buffer(
        self: object,
        in_data: object,
        frame_count: int,
        time_info: object,
        status_flags: object,
    ) -> object:
        
        self._buff.put(in_data)
        return None, pyaudio.paContinue

    def generator(self: object) -> object:
        while not self.closed:
            chunk = self._buff.get()
            if chunk is None:
                return
            data = [chunk]
            
            while True:
                try:
                    chunk = self._buff.get(block=False)
                    if chunk is None:
                        return
                    data.append(chunk)
                except queue.Empty:
                    break

            yield b"".join(data)
            
class Listener():
    isListening = False
    listener_thread = None

    def listen_print_loop(self, responses: object, callback) -> None:
        num_chars_printed = 0
        for response in responses:
            if not response.results:
                continue
            
            result = response.results[0]
            if not result.alternatives:
                continue

            transcript = result.alternatives[0].transcript

            callback(transcript)
        
            if self.isListening == False:
                return

    def listen(self, callback, language_code) -> None:
        
        client = speech.SpeechClient()
        
        config = speech.RecognitionConfig(
            encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
            sample_rate_hertz=RATE,
            language_code=language_code,
        )

        streaming_config = speech.StreamingRecognitionConfig(
            config=config, interim_results=True
        )

        with MicrophoneStream(RATE, CHUNK) as stream:
            audio_generator = stream.generator()
            requests = (
                speech.StreamingRecognizeRequest(audio_content=content)
                for content in audio_generator
            )

            responses = client.streaming_recognize(streaming_config, requests)
            
            self.listen_print_loop(responses, callback)
            
    def listen_in_background(self, callback, language_code):
        self.isListening = True
        
        def threaded_listen():
            self.listen(callback, language_code)
        
        def stopper(wait_for_stop=False):
            self.isListening = False
            if wait_for_stop:
                self.listener_thread.join()
                
        self.listener_thread = threading.Thread(target=threaded_listen)
        self.listener_thread.daemon = True
        self.listener_thread.start()
        return stopper