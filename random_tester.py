from __future__ import annotations
import unittest
from dataclasses import dataclass
from hypothesis import given, assume
import hypothesis.strategies as st
from typing import List, Optional, Union
from pprint import  pprint
import string
import subprocess
import re
import os
import sys


EXECUTABLE_NAME = "manageStudents"
EXECUTABLE_PATH = ""

def find_executable():
    global EXECUTABLE_PATH
    potential_paths = []
    if sys.platform == "win32":
        print("Tests can not be run under windows.", file=sys.stderr)
        sys.exit(-1)
    for root, dirs, files in os.walk(".."):
        if EXECUTABLE_NAME in files:
            potential_paths.append( os.path.abspath(os.path.join(root, EXECUTABLE_NAME)))

    if len(potential_paths) == 0:
        print(f"Couldn't find an executable 'manageStudents'! Make sure you compiled your program & placed this test"
              f" file within your project's directory or 1 folder inside it.", file=sys.stderr)
        sys.exit(-1)

    if len(potential_paths) > 1:
        print(f"Multiple 'manageStudents' executables found, can't tell which one to use, you should delete one of them!\n"
              f"Note that when building via CLion, the executable should appear at 'cmake_build_debug', \nwhereas when "
              f"building via GCC, it would appear where you invoked the command(usually at the exercise root directory)")
        sys.exit(-1)

    EXECUTABLE_PATH = potential_paths[0]
    print(f"Using executable at \"{EXECUTABLE_PATH}\"")

find_executable()

NORMAL_ALPHABET = string.ascii_lowercase + string.ascii_uppercase + '-'
NAME_ALPHABET = NORMAL_ALPHABET + ' '
MAX_FIELD_SIZE = 40


@st.composite
def gen_non_empty_name(draw) -> str:
    """ Generates a name, as long as it doesn't consist of whitespace """
    s = draw(st.text(alphabet=NAME_ALPHABET, min_size=1, max_size=MAX_FIELD_SIZE))
    adjusted = s.strip()  # dont begin or end with whitespace
    assume(len(adjusted) > 0)
    return adjusted

@dataclass
class Student:
    """ A valid/invalid student object """
    id: Optional[Union[int, str]]
    name: Optional[str]
    grade: Optional[Union[int, str]]
    age: Optional[Union[int, str]]
    country: Optional[str]
    city: Optional[str]

    def to_stdin_line(self) -> str:
        fields = '\t'.join(str(var) for var in vars(self).values())
        return f"{fields}\t"

    def __repr__(self):
        return self.to_stdin_line()

    @staticmethod
    @st.composite
    def valid_student(draw) -> Student:
        """ Generates a valid student """
        id = draw(st.integers(1000000000, 9999999999))
        name = draw(gen_non_empty_name())
        grade = draw(st.integers(0, 100))
        age = draw(st.integers(18, 120))
        country = draw(st.text(alphabet=NORMAL_ALPHABET, min_size=1, max_size=MAX_FIELD_SIZE))
        city = draw(st.text(alphabet=NORMAL_ALPHABET, min_size=1, max_size=MAX_FIELD_SIZE))

        
        stud = Student(id, name, grade, age, country, city)
        assume(len(stud.to_stdin_line()) <= 150) # ensure we didn't generate a student that is too long
        return stud


    @staticmethod
    @st.composite
    def invalid_student(draw, delete_fields=True, corrupt=True) -> Student:
        """ Creates an invalid student, which may have missing or invalid fields(as defined in the options)"""
        assert delete_fields or corrupt, "At least one of the options must be true"
        stud = draw(Student.valid_student())
        fields_to_invalidate = draw(st.sets(st.integers(0, 5), min_size=1, max_size=6))
        fields = vars(stud)
        fields_to_delete = set()
        for field_ix, (field_name, field_val) in enumerate(fields.items()):
            if field_ix in fields_to_invalidate:
                if delete_fields and (draw(st.booleans()) or not corrupt):
                    fields_to_delete.add(field_name)
                elif type(field_val) is str and corrupt:
                    setattr(stud, field_name,  invalidate_st(field_val, field_name, draw))
                elif type(field_val) is int and corrupt:
                    setattr(stud, field_name, invalidate_int(field_val, field_name, draw))

        for field_name in fields_to_delete:
            delattr(stud, field_name)

        assume(len(stud.to_stdin_line()) <= 150) # ensure we didn't generate a student that is too long
        return stud


ILLEGAL_CHARACTERS = list('!@#$%^&*()_+=/0123456789')

def invalidate_st(s: st, field: str, draw) -> str:
    """ Returns an invalid version of 's' with invalid characters in some places """
    out = ""
    indices_to_ruin = draw(st.sets(st.integers(min_value=0, max_value=len(s)-1), min_size=1, max_size=6))
    for ch in range(len(s)):
        if ch in indices_to_ruin:
            out += draw(st.sampled_from(ILLEGAL_CHARACTERS))
        else:
            out += s[ch]
    return out


def invalidate_int(i: int, field: str, draw) -> int:
    """ Returns an invalid verison of 'i', which might not even be an integer"""
    action = draw(st.integers(min_value=1, max_value=3))
    if action == 1:
        # create a negative number
        new_val = -i
        assume(new_val != 0)
    if action == 2:
        # create a very large/small integer
        new_val = draw(st.integers(min_value=-(2*15), max_value=(2*15 - 1)))
    if action == 3:
        # put a (non numerical) string instead of a number
        new_val = invalidate_st(str(i), field, draw)
        is_number = True
        try:
            _ = int(new_val)
        except ValueError:
            is_number = False
        # ensure we didn't accidentally generate string representation of an int
        assume(not is_number)

    # ensure we didn't accidentally generate something valid
    if field == "grade":
        assume(isinstance(new_val, str) or (new_val < 0 or new_val > 100))
    if field == "age":
        assume(isinstance(new_val, str) or (new_val < 18 or new_val > 120))
    if field == "id":
        assume(isinstance(new_val, str) or (new_val < 10**10 or new_val >= 10**11))
    return new_val


def students_to_str(s: List[Student]) -> str:
    """ Prints students in a format similar to what's used in the program """
    return "".join([f"{stud.to_stdin_line()}\n" for stud in s])


def students_to_input(s: List[Student]) -> str:
    """ Same as 'students_to_str' but with a quit symbol at the end, allowing it to be passed via STDIN to program. """
    return students_to_str(s) + "q\n"


def run_test(mode: str, inp: str) -> str:
    """ Runs the manageStudents executable in given mode and input, returning the process's stdout """
    proc = subprocess.run([EXECUTABLE_PATH, mode], text=True, capture_output=True, input=inp,
                          timeout=1000)
    if proc.stderr:
        print(f"There was an error running the manageStudents executable, or it writes to stderr(should only write to"
              f" stdout):\n{proc.stderr}")
        sys.exit(-1)
    return proc.stdout


class TestValidInputs(unittest.TestCase):
    # this is mostly a sanity check to ensure your program compiles, runs
    # and exits when given no input other than a quit message
    def test_prints_nothing_for_empty_input(self):
        result = run_test("best", "q\n")
        self.assertEqual(result, "Enter student info. To exit press q, then enter\n", "Shouldn't print anything when"
                                                                                      " given just quit message and"
                                                                                      " a linux newline")


        result = run_test("best", "q\r\n")
        self.assertEqual(result, "Enter student info. To exit press q, then enter\n", "Should also handle CRLF newlines"
                                                                                      " in quit message")

    @given(st.lists(Student.valid_student(), min_size=1))
    def test_can_find_the_best(self, s: List[Student]):

        result = run_test("best", students_to_input(s))
        found_best_st = re.search("^best student info is: (.*)$", result, re.MULTILINE)
        assert found_best_st is not None, "Your're not printing the best student properly"
        real_best = max(s, key=lambda stud: stud.grade/stud.age)

        print("While testing students: ")
        pprint(s)
        print("Result was: ")
        print(result)
        print("asserts:")
        self.assertEqual(real_best.to_stdin_line(), found_best_st.group(1), "Mismatch between expected best student"
                                                                            " and gotten best student")
        self.assertNotIn("ERROR: ", result, "There shouldn't be any error while inputting valid students")

    @given(st.lists(Student.valid_student(), min_size=1))
    def test_can_parse_with_windows_newlines(self, s: List[Student]):
        linux_input = students_to_str(s) + "q\n"
        windows_input = linux_input.replace('\n', '\r\n')
        result = run_test("best", windows_input)

        self.assertNotIn("\nERROR: ", result, "There shouldn't be any error when"
                                              " inputting valid students with CRLF newlines")

    @given(st.lists(Student.valid_student(), min_size=1))
    def test_can_stable_sort_grades(self, s: List[Student]):
        # python's sorting is stable, thus it should emit students in the exact order as your mergesort
        expected_sorted = sorted(s, key=lambda stud: stud.grade)
        expected_output = students_to_str(expected_sorted)
        result = run_test("merge", students_to_input(s))
        print("expected sort order: ")
        print(expected_output)
        print("gotten: ")
        print(result)
        self.assertIn(expected_output, result, "Students should appear (stable) sorted via grades in the output")
        self.assertNotIn("ERROR: ", result, "Shouldn't error while inserting valid students")

    @given(st.lists(Student.valid_student(), min_size=1, unique_by=lambda s: s.name))
    def test_can_quicksort_names(self, s: List[Student]):
        # this time we have no duplicate names, so stability of sort isn't tested
        expected_sorted = sorted(s, key=lambda stud: stud.name)

        expected_output = students_to_str(expected_sorted)
        result = run_test("quick", students_to_input(s))
        print("expected sort order: ")
        print(expected_output)
        print("gotten: ")
        print(result)
        self.assertIn(expected_output, result, "Students should appear (stable) sorted via grades in the output")
        self.assertNotIn("ERROR: ", result, "Shouldn't error while inserting valid students")



class TestInvalidInputs(unittest.TestCase):
    def __errors_when_encountering_invalid_student(self, s: Student, data: st.data):
        print(f"Inserting invalid \"{s}\"")
        mode = data.draw(st.sampled_from(['best', 'quick', 'merge']))
        res = run_test(mode, s.to_stdin_line()+"\nq\n")
        self.assertIn("\nERROR: ", res, f"Expected error for student:\n{repr(s)}")

    @given(Student.invalid_student(corrupt=False, delete_fields=True), st.data())
    def test_errors_when_encountering_missing_fields(self, s: Student, data: st.data):
        self.__errors_when_encountering_invalid_student(s, data)

    @given(Student.invalid_student(corrupt=True, delete_fields=False), st.data())
    def test_errors_when_encountering_corrupt_fields(self, s: Student, data: st.data):
        self.__errors_when_encountering_invalid_student(s, data)

    @given(Student.invalid_student(corrupt=True, delete_fields=True), st.data())
    def test_errors_when_encoutnering_corrupt_or_missing_fields(self, s: Student, data: st.data):
        """ Combination of above tests """
        self.__errors_when_encountering_invalid_student(s, data)

