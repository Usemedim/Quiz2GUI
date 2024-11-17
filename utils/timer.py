import time

class Timer:
    def __init__(self, total_duration):
        self.total_duration = total_duration
        self.start_time = None
        self.end_time = None
        self.running = False

    def start(self):
        """Timer'ı başlatır."""
        self.start_time = time.time()
        self.end_time = self.start_time + self.total_duration
        self.running = True

    def stop(self):
        """Timer'ı durdurur."""
        self.running = False

    def get_remaining_time(self):
        """Kalan süreyi döndürür (saniye cinsinden)."""
        if not self.running:
            return 0
        remaining_time = self.end_time - time.time()
        return max(0, remaining_time)

    def is_time_up(self):
        """Sürenin dolup dolmadığını kontrol eder."""
        return self.get_remaining_time() <= 0

