# Dependency Injection (Azure Credentials)
from azure.identity import DefaultAzureCredential
from core.logger import get_logger

logger = get_logger(__name__)

# Global variable to cache the credential instance
_credential_instance = None

def get_azure_credential() -> DefaultAzureCredential:
    """
    Provides a singleton instance of DefaultAzureCredential.
    Safely handles authentication for Workload Identity in AKS or Local CLI.
    """
    global _credential_instance
    
    if _credential_instance is None:
        try:
            logger.info("Initializing DefaultAzureCredential...")
            _credential_instance = DefaultAzureCredential()
            logger.info("Azure Credential initialized successfully.")
        except Exception as e:
            logger.error("Failed to initialize Azure Credentials", exc_info=True)
            raise RuntimeError(f"Credential initialization failed: {str(e)}")
            
    return _credential_instance