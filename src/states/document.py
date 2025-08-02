from aiogram.fsm.state import StatesGroup, State


class PDFToWordState(StatesGroup):
    waiting_for_pdf = State()


class WordToPDFState(StatesGroup):
    waiting_for_word = State()


class ImageToPDFState(StatesGroup):
    waiting_for_images = State()


class PDFToPNGState(StatesGroup):
    waiting_for_pdf = State()
