from datetime import datetime

class Utils:
    @staticmethod
    def format_datetime(dt: datetime) -> str:
        return dt.strftime("%Y-%m-%d %H:%M:%S")

    @staticmethod
    def parse_datetime(date_str: str) -> datetime:
        return datetime.strptime(date_str, "%Y-%m-%d")
