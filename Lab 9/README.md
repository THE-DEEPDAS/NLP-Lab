on observing the merges i noticed that the data is very much corrupted, there are merges of "gujarati", "hindi" and "english" and "chinese" on the top merges so the result on test data sample which i have given is not so good.

Also some words did get merged like "kar in gujarati" and some other gujarati words.

some new regex learned:
(?<...) → Lookbehind
Look behind the current position, but don’t consume any characters.

(?<=...) → positive lookbehind (something must be there)
(?<!...) → negative lookbehind (something must not be there)