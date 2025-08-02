from aiogram import Router
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from src.states.document import ImageToPDFState


router = Router()


@router.message(ImageToPDFState.waiting_for_images)
async def process_image_to_pdf(message: Message, state: FSMContext):
    pass
