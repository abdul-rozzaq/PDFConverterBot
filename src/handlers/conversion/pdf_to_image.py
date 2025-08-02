from aiogram import Router

from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from src.states.document import PDFToPNGState


router = Router()


@router.message(PDFToPNGState.waiting_for_pdf)
async def process_pdf_to_png(message: Message, state: FSMContext):
    pass
