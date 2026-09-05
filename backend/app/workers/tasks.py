"""Punto de extensión para el perfilado de archivos subidos.

La tarea se registra ahora; la lectura del objeto y el perfil Polars se agrega
cuando el flujo de carga finalice con comprobación de existencia en Storage.
"""
from app.workers.celery_app import celery_app


@celery_app.task(bind=True, autoretry_for=(Exception,), retry_backoff=True, max_retries=3)
def profile_dataset(self, dataset_id: str) -> None:
    """Reserva una tarea durable para perfilado; no procesa datos en el request HTTP."""
    # La implementación del lector de CSV/XLSX vivirá aquí en el siguiente incremento.
    return None
