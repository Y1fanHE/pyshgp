"""The :mod:`atoms` module defines all types of Push Atoms.

An Atom is a peice of code in the Push language. A Literal Atom is a constant
value of one of the supported PushType. An Instruction Atom is a wrapped
function that can be used to manipulate a PushState. A CodeBlock is a sequence
of other Atoms is used to express nested expressions of code.
"""
from __future__ import annotations
from typing import Sequence, Tuple
from itertools import chain, count

from pyrsistent import PClass, field, CheckedPVector

from pyshgp.push.types import PushType


class Atom:
    """Base class of all Atoms. The fundamental element of Push programs."""
    ...


class Closer(Atom, PClass):
    """An Atom dedicated to denoting the close of a CodeBlock in its flat representsion."""
    ...


class Literal(Atom, PClass):
    """An Atom which holds a constant value.

    Attributes
    ----------
    value : Any
        The value to be stored in Literal.
    push_type : PushType, optional
        The PushType of the Literal. Usually, the PushType's underlying native
        type is the same as the type of the Literal's value. The PushType is
        used to determine how to route the Literal onto the correct PushStack
        of the PushState during program execution. If push_type is none, the
        PushType will attempt to be inferred from the type of the value.

    """
    __invariant__ = lambda l: (l.push_type.is_instance(l.value), "Value is not of PushType.")
    value = field(mandatory=True)
    push_type = field(type=PushType, mandatory=True)


class InstructionMeta(Atom, PClass):
    """An identifier of a Push Instruction.

    The InstructionMeta is a placeholder atom. When a PushInterpreter evaluates
    an instruction ID, it searches for an instruction with the given
    name in its InstructionSet. If found, this instruction is evaluated by the PushInterpreter.

    Parameters
    ----------
    name: str
        The name of the Instruction being referenced.

    """
    name = field(type=str, mandatory=True)
    code_blocks = field(type=int, mandatory=True)


class Input(Atom, PClass):
    input_index = field(type=int, mandatory=True)


class CodeBlock(Atom, CheckedPVector):
    __type__ = Atom

    def size(self, depth: int = 1) -> int:
        """Return the size of the block and the size of all the nested blocks."""
        return sum([el.size(depth + 1) + 1 if isinstance(el, CodeBlock) else 1 for el in self])

    def depth(self) -> int:
        """Return the farthest depth of the CodeBlock."""
        i = iter(self)
        level = 0
        try:
            for level in count():
                i = chain([next(i)], i)
                i = chain.from_iterable(s for s in i if isinstance(s, Sequence) and not isinstance(s, str))
        except StopIteration:
            return level
        return 0

    def code_at_point(self, ndx: int) -> Atom:
        """Return a nested element of the CodeBlock using depth first traversal."""
        if ndx == 0:
            return self
        i = ndx
        for el in self:
            i = i - 1
            if i == 0:
                return el
            if isinstance(el, CodeBlock):
                next_depth = el.code_at_point(i)
                if next_depth is not None:
                    return next_depth
                i = i - el.size()

    def with_code_inserted_at_point(self, code: Atom, index: int) -> CodeBlock:
        """Insert an element into the CodeBlock using depth first traversal."""
        if index > self.size():
            return self.append(code)
        _, new = self._attempt_code_insert(code, index)
        return new

    def _attempt_code_insert(self, code: Atom, index: int) -> Tuple[bool, CodeBlock]:
        i = index
        for idx, el in enumerate(self):
            if i == 0:
                new = CodeBlock(self[:idx] + [code] + self[idx:])
                return True, new
            if isinstance(el, CodeBlock):
                inserted, new = el._attempt_code_insert(code, i - 1)
                if inserted:
                    return True, self.set(idx, new)
                i = i - (el.size() + 1)
            i = i - 1
        if i == 0:
            return True, self.append(code)
        return False, self

    # def insert_code_at_point(self, code: Atom, index: int):
    #     """Insert an element into the CodeBlock using depth first traversal."""
    #     i = index
    #     for ndx, el in enumerate(self):
    #         if i == 0:
    #             self.insert(ndx, code)
    #             return self
    #         i = i - 1
    #         if isinstance(el, CodeBlock):
    #             next_depth = el.insert_code_at_point(code, i)
    #             if next_depth is not None:
    #                 return self
    #             i = i - el.size()
