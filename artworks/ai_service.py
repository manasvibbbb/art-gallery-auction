import requests
import json
from django.conf import settings
import logging
import base64

logger = logging.getLogger(__name__)


class StabilityAIService:
    """Service to interact with Stability AI API"""

    BASE_URL = "https://api.stability.ai/v1"

    def __init__(self):
        self.api_key = settings.STABLE_DIFFUSION_API_KEY
        self.headers = {
            'authorization': f'Bearer {self.api_key}',
            'accept': 'application/json',
        }

    def get_valid_dimensions(self, width):
        """
        SDXL only accepts specific dimensions.
        Valid sizes: 1024x1024, 1152x896, 1216x832, 1344x768, 1536x640,
                     640x1536, 768x1344, 832x1216, 896x1152
        """
        valid_dimensions = {
            512: (832, 1216),  # Smaller size - portrait
            768: (1152, 896),  # Medium size - landscape
            1024: (1024, 1024),  # Standard square
        }
        return valid_dimensions.get(width, (1024, 1024))

    def generate_image(self, prompt, style='realistic', width=512):
        """
        Generate an image using Stability AI

        Args:
            prompt (str): Description of the image to generate
            style (str): Art style (realistic, oil_painting, etc.)
            width (int): Image width (512, 768, or 1024)

        Returns:
            dict: Response with image data or error
        """

        if not self.api_key:
            return {
                'success': False,
                'error': 'API key not configured. Add STABLE_DIFFUSION_API_KEY to settings.py'
            }

        # Map style to prompt enhancement
        style_prompts = {
            'realistic': 'photorealistic, highly detailed, professional photography',
            'oil_painting': 'oil painting, impressionist, brushstrokes',
            'digital_art': 'digital art, high resolution, concept art',
            'watercolor': 'watercolor painting, soft colors, artistic',
            'anime': 'anime style, vibrant colors, manga illustration',
            'cartoon': 'cartoon style, fun, colorful, playful',
            'sketch': 'pencil sketch, line art, detailed drawing',
            'cyberpunk': 'cyberpunk, neon lights, futuristic, sci-fi',
            'fantasy': 'fantasy art, magical, mystical, epic',
        }

        # Enhance prompt with style
        enhanced_prompt = f"{prompt}, {style_prompts.get(style, 'detailed')}"

        try:
            # Use SDXL - the only model your account has access to
            url = f"{self.BASE_URL}/generation/stable-diffusion-xl-1024-v1-0/text-to-image"

            # Get valid dimensions for SDXL
            img_width, img_height = self.get_valid_dimensions(width)

            logger.debug(f"🎨 Generating image with prompt: '{prompt}'")
            logger.debug(f"📐 Using model: stable-diffusion-xl-1024-v1-0")
            logger.debug(f"📏 Dimensions: {img_width}x{img_height}")

            data = {
                "text_prompts": [
                    {
                        "text": enhanced_prompt,
                        "weight": 1
                    }
                ],
                "cfg_scale": 7,
                "height": img_height,
                "width": img_width,
                "samples": 1,
                "steps": 30,
            }

            response = requests.post(
                url,
                headers=self.headers,
                json=data,
                timeout=120
            )

            logger.debug(f"Response status: {response.status_code}")

            # Check for errors
            if response.status_code != 200:
                error_msg = f"API request failed: {response.status_code} {response.reason}"

                try:
                    error_data = response.json()
                    if isinstance(error_data, dict):
                        error_msg = f"API Error: {error_data.get('message', str(error_data))}"
                except:
                    error_msg += f" - {response.text[:300]}"

                logger.error(f"API Error: {error_msg}")
                return {
                    'success': False,
                    'error': error_msg
                }

            # Parse response
            result = response.json()

            if 'artifacts' in result and len(result['artifacts']) > 0:
                # Image data is base64 encoded
                image_data = result['artifacts'][0].get('base64')

                if image_data:
                    logger.info(f"✅ Image generated successfully")
                    return {
                        'success': True,
                        'image_base64': image_data,
                        'prompt': enhanced_prompt,
                        'style': style,
                    }

            return {
                'success': False,
                'error': 'No image generated in response. Please try again.'
            }

        except requests.exceptions.Timeout:
            logger.error("Request timeout")
            return {
                'success': False,
                'error': 'Request timed out. Image generation took too long. Please try again.'
            }

        except requests.exceptions.RequestException as e:
            logger.error(f"Network error: {str(e)}")
            return {
                'success': False,
                'error': f'Network error: {str(e)}'
            }

        except Exception as e:
            logger.error(f"Error generating image: {str(e)}")
            return {
                'success': False,
                'error': f'Error generating image: {str(e)}'
            }


def generate_ai_image(prompt, style='realistic', width=512):
    """Helper function to generate image"""
    service = StabilityAIService()
    return service.generate_image(prompt, style, width)
