A generator is a special type of iterator in Python that allows you to iterate over a sequence of values, but instead of storing all values in memory at once, it generates them on the fly, one at a time, as you need them.

Generators are created using functions with the yield keyword or by using generator expressions.

Each time you call next() on a generator, it resumes where it left off and yields the next value.

__iter__ makes class an iterator/generator.
if total_chars > self.char_limit: If the buffer exceeds the character limit:
yield "".join(buffer): Yields the current chunk as a single string (returns it to the caller, but remembers where it left off).