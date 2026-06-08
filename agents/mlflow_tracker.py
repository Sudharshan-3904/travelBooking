try:
    import mlflow
except ImportError:
    mlflow = None

class MLflowTracker:
    def __init__(self, experiment_name: str = "TravelNet Phase0 Baseline"):
        self.experiment_name = experiment_name
        if mlflow:
            mlflow.set_tracking_uri("sqlite:///mlflow.db")
            mlflow.set_experiment(self.experiment_name)
            self.run = mlflow.start_run(run_name=self.experiment_name)
        else:
            self.run = None

    def log_params(self, params: dict) -> None:
        if self.run is not None:
            mlflow.log_params(params)

    def log_metrics(self, metrics: dict) -> None:
        if self.run is not None:
            mlflow.log_metrics(metrics)

    def end_run(self) -> None:
        if self.run is not None:
            mlflow.end_run()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.end_run()
