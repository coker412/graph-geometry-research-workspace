#!/usr/bin/env python3
"""Offline link checks and exact arithmetic for the local Hessian teaching example."""

from fractions import Fraction as Q
import json
from pathlib import Path
import re


def determinant(matrix):
    rows = [[Q(x) for x in row] for row in matrix]
    result = Q(1)
    for i in range(len(rows)):
        pivot = next((j for j in range(i, len(rows)) if rows[j][i]), None)
        if pivot is None:
            return Q(0)
        if pivot != i:
            rows[i], rows[pivot] = rows[pivot], rows[i]
            result = -result
        value = rows[i][i]
        result *= value
        for j in range(i + 1, len(rows)):
            ratio = rows[j][i] / value
            rows[j] = [a - ratio * b for a, b in zip(rows[j], rows[i])]
    return result


def quadratic(matrix, vector):
    return sum(vector[i] * matrix[i][j] * vector[j]
               for i in range(len(vector)) for j in range(len(vector)))


def scaled_hessian(f, gradient, hessian, t):
    # B = u^3 D^2u; u^2 = f^2+t^2. All arithmetic stays rational.
    m = len(gradient)
    u2 = f * f + t * t
    rows = [[f * u2 * hessian[i][j] + t*t*gradient[i]*gradient[j]
             for j in range(m)] + [-f*t*gradient[i]] for i in range(m)]
    rows.append([-f*t*g for g in gradient] + [f*f])
    return rows


def main():
    root = Path(__file__).resolve().parent
    for page in root.glob('*.md'):
        text = page.read_text()
        assert not any(ord(c) < 32 and c not in '\t\n\r' for c in text), page.name
        for target in re.findall(r'\[[^\]]*\]\(([^)]+)\)', text):
            if target.startswith(('https://', 'http://', '#')):
                continue
            assert (page.parent / target.split('#', 1)[0]).exists(), (page.name, target)
    sources = json.loads((root / 'sources.json').read_text())
    for source in sources['sources']:
        assert len(source['quoted_excerpt'].split()) <= 25
        assert re.fullmatch('[0-9a-f]{64}', source['pdf_sha256'])
        assert source['version'] in source['pdf_url']

    cases = 0
    for m in (1, 2, 3):
        for seed in range(4):
            f = Q(seed + 1, 2)
            gradient = [Q(i-seed, 3) for i in range(m)]
            q = [Q(i+seed+1, 4) for i in range(m)]
            h = [[Q(i == j) + q[i]*q[j] for j in range(m)] for i in range(m)]
            for t in map(Q, (-3, -1, 0, 1, 3)):
                b = scaled_hessian(f, gradient, h, t)
                assert determinant(b) == f**(m+2) * (f*f+t*t)**m * determinant(h)
                vectors = [[Q(i == j) for i in range(m+1)] for j in range(m+1)]
                vectors.append([Q(i+1) for i in range(m+1)])
                for vector in vectors:
                    xi, tau = vector[:-1], vector[-1]
                    dot = sum(a*c for a, c in zip(gradient, xi))
                    squares = f*(f*f+t*t)*quadratic(h, xi) + (f*tau-t*dot)**2
                    assert quadratic(b, vector) == squares > 0
                cases += 1

    b = scaled_hessian(Q(2), [Q(2)], [[Q(2)]], Q(2))
    assert b == [[48, -8], [-8, 4]]
    assert determinant(b) / Q(8)**3 == Q(1, 4)
    assert quadratic(b, [1, 2]) == 32
    assert quadratic(b, [0, 1]) == 4
    assert determinant([[b[0][0], 0], [0, b[1][1]]]) != determinant(b)
    flat = scaled_hessian(Q(1), [Q(0)], [[Q(0)]], Q(2))
    assert determinant(flat) == quadratic(flat, [1, 0]) == 0
    print(f'Examples passed: links, source metadata, {cases} exact Hessian cases, '
          'worked 2D matrix, and missing-mixed-term/flat-direction controls. '
          'Finite computations do not certify the source papers.')


if __name__ == '__main__':
    main()
