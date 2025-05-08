import os
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List

class ResultsManager:
    def __init__(self, base_dir: str = "results"):
        self.base_dir = Path(base_dir)
        self.date_dir = self._create_date_directory()
        self.session_dir = self._create_session_directory()
        self._setup_logging()
        self._create_subdirectories()
        
    def _create_date_directory(self) -> Path:
        """Создает директорию с датой для всех сессий"""
        date_str = datetime.now().strftime("%Y-%m-%d")
        date_dir = self.base_dir / date_str
        date_dir.mkdir(parents=True, exist_ok=True)
        return date_dir
    
    def _create_session_directory(self) -> Path:
        """Создает директорию для текущей сессии с временной меткой"""
        timestamp = datetime.now().strftime("%H%M%S")
        session_dir = self.date_dir / f"session_{timestamp}"
        session_dir.mkdir(parents=True, exist_ok=True)
        return session_dir
    
    def _setup_logging(self):
        """Настраивает систему логирования"""
        log_file = self.session_dir / "main.log"
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger("ResultsManager")
    
    def _create_subdirectories(self):
        """Создает поддиректории для различных типов данных"""
        self.directories = {
            "shots": self.session_dir / "shots",
            "hits": self.session_dir / "hits",
            "target_detections": self.session_dir / "target_detections",
            "predictions": self.session_dir / "predictions",
            "misses": self.session_dir / "misses",
            "difficulties": self.session_dir / "difficulties",
            "metrics": self.session_dir / "metrics",
            "screenshots": self.session_dir / "screenshots"
        }
        
        for dir_path in self.directories.values():
            dir_path.mkdir(exist_ok=True)
    
    def log_shot(self, shot_data: Dict[str, Any]):
        """Логирует информацию о выстреле"""
        timestamp = datetime.now().strftime("%H%M%S_%f")
        file_path = self.directories["shots"] / f"shot_{timestamp}.json"
        self._save_json(file_path, shot_data)
        self.logger.info(f"Shot logged: {shot_data}")
    
    def log_hit(self, hit_data: Dict[str, Any]):
        """Логирует информацию о попадании"""
        timestamp = datetime.now().strftime("%H%M%S_%f")
        file_path = self.directories["hits"] / f"hit_{timestamp}.json"
        self._save_json(file_path, hit_data)
        self.logger.info(f"Hit logged: {hit_data}")
    
    def log_target_detection(self, detection_data: Dict[str, Any]):
        """Логирует информацию об обнаружении цели"""
        timestamp = datetime.now().strftime("%H%M%S_%f")
        file_path = self.directories["target_detections"] / f"detection_{timestamp}.json"
        self._save_json(file_path, detection_data)
        self.logger.info(f"Target detection logged: {detection_data}")
    
    def log_prediction(self, prediction_data: Dict[str, Any]):
        """Логирует информацию о предсказании движения"""
        timestamp = datetime.now().strftime("%H%M%S_%f")
        file_path = self.directories["predictions"] / f"prediction_{timestamp}.json"
        self._save_json(file_path, prediction_data)
        self.logger.info(f"Prediction logged: {prediction_data}")
    
    def log_miss(self, miss_data: Dict[str, Any]):
        """Логирует информацию о промахе"""
        timestamp = datetime.now().strftime("%H%M%S_%f")
        file_path = self.directories["misses"] / f"miss_{timestamp}.json"
        self._save_json(file_path, miss_data)
        self.logger.info(f"Miss logged: {miss_data}")
    
    def log_difficulty(self, difficulty_data: Dict[str, Any]):
        """Логирует информацию о сложности ситуации"""
        timestamp = datetime.now().strftime("%H%M%S_%f")
        file_path = self.directories["difficulties"] / f"difficulty_{timestamp}.json"
        self._save_json(file_path, difficulty_data)
        self.logger.info(f"Difficulty logged: {difficulty_data}")
    
    def save_metrics(self, metrics_data: Dict[str, Any]):
        """Сохраняет метрики производительности"""
        timestamp = datetime.now().strftime("%H%M%S")
        file_path = self.directories["metrics"] / f"metrics_{timestamp}.json"
        self._save_json(file_path, metrics_data)
        self.logger.info(f"Metrics saved: {metrics_data}")
    
    def save_screenshot(self, screenshot_data: bytes, metadata: Dict[str, Any]):
        """Сохраняет скриншот с метаданными"""
        timestamp = datetime.now().strftime("%H%M%S_%f")
        screenshot_path = self.directories["screenshots"] / f"screenshot_{timestamp}.png"
        metadata_path = self.directories["screenshots"] / f"screenshot_{timestamp}_metadata.json"
        
        with open(screenshot_path, "wb") as f:
            f.write(screenshot_data)
        self._save_json(metadata_path, metadata)
        self.logger.info(f"Screenshot saved: {metadata}")
    
    def _save_json(self, file_path: Path, data: Dict[str, Any]):
        """Сохраняет данные в JSON файл"""
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
    
    def get_session_summary(self) -> Dict[str, Any]:
        """Возвращает сводку по текущей сессии"""
        summary = {
            "date": self.date_dir.name,
            "session_start": self.session_dir.name,
            "total_shots": len(list(self.directories["shots"].glob("*.json"))),
            "total_hits": len(list(self.directories["hits"].glob("*.json"))),
            "total_misses": len(list(self.directories["misses"].glob("*.json"))),
            "total_detections": len(list(self.directories["target_detections"].glob("*.json"))),
            "total_predictions": len(list(self.directories["predictions"].glob("*.json"))),
            "total_difficulties": len(list(self.directories["difficulties"].glob("*.json"))),
            "total_screenshots": len(list(self.directories["screenshots"].glob("*.png")))
        }
        
        # Сохраняем сводку
        summary_path = self.session_dir / "session_summary.json"
        self._save_json(summary_path, summary)
        return summary 