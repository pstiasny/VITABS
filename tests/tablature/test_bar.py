from fractions import Fraction

from vitabs.tablature import Bar, Chord


def test_real_duration():
    bar = Bar()
    assert bar.real_duration() == Fraction(1, 4)

    bar.chords = [
        Chord(Fraction(1, 8)),
        Chord(Fraction(1, 4)),
        Chord(Fraction(1, 4)),
    ]
    assert bar.real_duration() == Fraction(5, 8)

    bar.chords = [
        Chord(Fraction(1, 3)),
        Chord(Fraction(1, 4)),
        Chord(Fraction(1, 4)),
    ]
    assert bar.real_duration() == Fraction(5, 6)


def test_gcd():
    bar = Bar()
    assert bar.gcd() == 4

    bar.chords = [
        Chord(Fraction(1, 8)),
        Chord(Fraction(1, 4)),
        Chord(Fraction(1, 4)),
    ]
    assert bar.gcd() == 8

    bar.chords = [
        Chord(Fraction(1, 3)),
        Chord(Fraction(1, 4)),
        Chord(Fraction(1, 4)),
    ]
    assert bar.gcd() == 12


def test_total_width():
    bar = Bar()
    assert bar.total_width() == 5

    bar.chords = [
        Chord(Fraction(1, 8)),
        Chord(Fraction(1, 4)),
        Chord(Fraction(1, 4)),
    ]
    assert bar.total_width() == 15

    bar.chords = [
        Chord(Fraction(1, 3)),
        Chord(Fraction(1, 4)),
        Chord(Fraction(1, 4)),
    ]
    assert bar.total_width() == 25
