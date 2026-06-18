import logging
import torch

logger = logging.getLogger(__name__)

class UniversalStandardizer:
    """
    Standardizes physical radiometric satellite data into unified AI-ready tensors.
    Ensures that irrespective of the satellite source, the model receives uniformly 
    scaled inputs.
    """

    @staticmethod
    def normalize_bt(bt_tensor: torch.Tensor, min_bt: float = 180.0, max_bt: float = 330.0) -> torch.Tensor:
        """
        Clips Brightness Temperature (K) and normalizes it to a [0, 1] range.

        Args:
            bt_tensor (torch.Tensor): The physical brightness temperature tensor in Kelvin.
            min_bt (float, optional): Lower bound for clipping (typically overshooting tops). Defaults to 180.0.
            max_bt (float, optional): Upper bound for clipping (typically hot desert). Defaults to 330.0.

        Returns:
            torch.Tensor: Normalized tensor bounded strictly between [0, 1].
        """
        logger.debug(f"Normalizing tensor of shape {bt_tensor.shape} with bounds [{min_bt}K, {max_bt}K]")
        
        # Apply min-max normalization
        bt_norm = (bt_tensor - min_bt) / (max_bt - min_bt)
        
        # Clip values strictly between 0 and 1
        bt_norm = torch.clamp(bt_norm, 0.0, 1.0)
        
        # Clean any remaining NaNs or Infs that might have survived the math
        bt_norm = torch.nan_to_num(bt_norm, nan=0.0, posinf=1.0, neginf=0.0)
        
        return bt_norm