import pyaudio
import wave

def play_wav_file(file_path):
    # WAV 파일 열기
    wf = wave.open(file_path, 'rb')

    # PyAudio 객체 생성
    p = pyaudio.PyAudio()

    # 스트림 열기
    stream = p.open(
        format=p.get_format_from_width(wf.getsampwidth()),  # 샘플 폭 가져오기
        channels=wf.getnchannels(),                        # 채널 수 가져오기
        rate=wf.getframerate(),                            # 프레임 레이트 가져오기
        output=True                                        # 출력 스트림으로 설정
    )

    # 데이터 읽고 재생
    chunk = 1024  # 한번에 읽을 프레임 수
    data = wf.readframes(chunk)
    print("재생 중... 'Ctrl+C'로 종료하세요.")
    try:
        while data:
            stream.write(data)  # 스트림에 데이터 쓰기 (재생)
            data = wf.readframes(chunk)
    except KeyboardInterrupt:
        print("\n재생 중단됨.")
    finally:
        # 스트림 닫기
        stream.stop_stream()
        stream.close()
        wf.close()
        p.terminate()

# 실행
play_wav_file("test.wav")