from random import randint
from time import sleep
from collections import deque
from .models import Piece, Order
from threading import Thread, Lock, Event
import sqlalchemy
from . import Session


class Machine(Thread):
    STATUS_WAITING = "Waiting"
    STATUS_CHANGING_PIECE = "Changing Piece"
    STATUS_WORKING = "Working"
    __stauslock__ = Lock()
    thread_session = None

    def __init__(self):
        Thread.__init__(self)
        self.queue = deque([])
        self.working_piece = None
        self.status = Machine.STATUS_WAITING
        self.instance = self
        self.queue_not_empty_event = Event()
        self.reload_pieces_at_startup()
        self.start()

    def reload_pieces_at_startup(self):
        try:
            self.thread_session = Session()
            manufacturing_piece = self.thread_session.query(Piece).filter_by(status=Piece.STATUS_MANUFACTURING).first()
            if manufacturing_piece:
                self.add_piece_to_queue(manufacturing_piece)

            queued_pieces = self.thread_session.query(Piece).filter_by(status=Piece.STATUS_QUEUED).all()
            if queued_pieces:
                self.add_pieces_to_queue(queued_pieces)
            self.thread_session.close()
        except (sqlalchemy.exc.ProgrammingError, sqlalchemy.exc.OperationalError):
            print("Error getting Queued/Manufacturing Pieces at startup. It may be the first execution")

    def run(self):
        while True:
            self.queue_not_empty_event.wait()
            print("Thread notified that queue is not empty.")
            self.thread_session = Session()

            while self.queue.__len__() > 0:
                self.instance.create_piece()

            self.queue_not_empty_event.clear()
            print("Lock thread because query is empty.")

            self.instance.status = Machine.STATUS_WAITING
            self.thread_session.close()

    def create_piece(self):
        # Get piece from queue
        piece_ref = self.queue.popleft()

        # Machine and piece status updated during manufacturing
        self.working_piece = self.thread_session.query(Piece).get(piece_ref)

        # Machine and piece status updated before manufacturing
        self.working_piece_to_manufacturing()

        # Simulate piece is being manufactured
        sleep(randint(5, 20))

        # Machine and piece status updated after manufacturing
        self.working_piece_to_finished()

        self.working_piece = None

    def working_piece_to_manufacturing(self):
        self.status = Machine.STATUS_WORKING
        self.working_piece.status = Piece.STATUS_MANUFACTURING
        self.thread_session.commit()
        self.thread_session.flush()

    def working_piece_to_finished(self):
        self.instance.status = Machine.STATUS_CHANGING_PIECE
        self.working_piece.status = Piece.STATUS_MANUFACTURED

        order_finished = True
        for piece in self.working_piece.order.pieces:
            if piece.status != Piece.STATUS_MANUFACTURED:
                order_finished = False
        if order_finished:
            self.working_piece.order.status = Order.STATUS_FINISHED

        self.thread_session.commit()
        self.thread_session.flush()

    def add_pieces_to_queue(self, pieces):
        for piece in pieces:
            self.add_piece_to_queue(piece)

    def add_piece_to_queue(self, piece):
        self.queue.append(piece.ref)
        piece.status = Piece.STATUS_QUEUED
        print("Adding piece to queue: {}".format(piece.ref))
        self.queue_not_empty_event.set()

    def remove_pieces_from_queue(self, pieces):
        for piece in pieces:
            if piece.status == Piece.STATUS_QUEUED:
                self.queue.remove(piece.ref)
                piece.status = Piece.STATUS_CANCELLED



