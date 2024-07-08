import unittest
from unittest.mock import patch, MagicMock
from your_repository_module import NoteRepository, Note, add_note, update_note, delete_note

class TestNoteRepository(unittest.TestCase):

    def setUp(self):
        self.mock_note_repository = MagicMock(spec=NoteRepository)
        self.note_data = {
            'title': 'Test Note',
            'content': 'This is a test note'
        }

    def test_add_note(self):
        # Mocking the behavior of NoteRepository.add_note
        self.mock_note_repository.add_note.return_value = True
        
        result = add_note(self.note_data)
        self.assertTrue(result, "Failed to add note")

    def test_update_note(self):
        # Mocking the behavior of NoteRepository.update_note
        note_id = 1
        updated_data = {
            'id': note_id,
            'title': 'Updated Note',
            'content': 'Updated content'
        }
        self.mock_note_repository.update_note.return_value = True
        
        result = update_note(updated_data)
        self.assertTrue(result, "Failed to update note")

    def test_delete_note(self):
        # Mocking the behavior of NoteRepository.delete_note
        note_id = 1
        self.mock_note_repository.delete_note.return_value = True
        
        result = delete_note(note_id)
        self.assertTrue(result, "Failed to delete note")

if __name__ == '__main__':
    unittest.main()

    
    