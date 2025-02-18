import time
import logging
from dataclasses import dataclass
from typing import Dict, Any

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class TimeMetrics:
    download_time: float = 0.0
    parse_time: float = 0.0
    analysis_time: float = 0.0
    total_time: float = 0.0
    review_count: int = 0


class TimeAnalyzer:
    def __init__(self):
        self.start_time = None
        self.metrics = TimeMetrics()

    def start(self):
        """Start the total time measurement"""
        self.start_time = time.time()
        return self

    def measure_operation(self, operation_name: str) -> float:
        """Context manager for measuring operation time"""

        class TimeMeasurer:
            def __init__(self, analyzer, operation):
                self.analyzer = analyzer
                self.operation = operation
                self.start_time = None

            def __enter__(self):
                self.start_time = time.time()
                return self

            def __exit__(self, exc_type, exc_val, exc_tb):
                duration = time.time() - self.start_time
                setattr(self.analyzer.metrics, f"{self.operation}_time", duration)
                logger.info(
                    f"{self.operation.title()} completed in {duration:.2f} seconds"
                )

        return TimeMeasurer(self, operation_name)

    def set_review_count(self, count: int):
        """Set the number of reviews processed"""
        self.metrics.review_count = count

    def finalize(self) -> Dict[str, Any]:
        """Finalize the timing analysis and return metrics"""
        if self.start_time is None:
            raise RuntimeError("Timer was not started")

        self.metrics.total_time = time.time() - self.start_time

        return {
            "download_time": f"{self.metrics.download_time:.2f}",
            "parse_time": f"{self.metrics.parse_time:.2f}",
            "analysis_time": f"{self.metrics.analysis_time:.2f}",
            "total_time": f"{self.metrics.total_time:.2f}",
            "review_count": self.metrics.review_count,
        }


# Example usage:
# timer = TimeAnalyzer().start()
# with timer.measure_operation("download"):
#     # download operation
# with timer.measure_operation("parse"):
#     # parse operation
# timer.set_review_count(len(reviews))
# stats = timer.finalize()
