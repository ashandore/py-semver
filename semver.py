import re

version_regex = r"\s*=?[vV]?\s*(?P<major>[0-9]+)\.(?P<minor>[0-9]+)\.(?P<patch>[0-9]+)(?:-?(?P<prerelease>[0-9a-zA-Z_.-]+))?(?:\+(?P<build>[0-9a-zA-Z_.-]+))?"
spec_version_regex = r"\s*=?[vV]?\s*(?P<major>[0-9xX*]+)(?:\.(?P<minor>[0-9xX*]+))?(?:\.(?P<patch>[0-9xX*]+))?(?:-?(?P<prerelease>[0-9a-zA-Z_.-]+))?(?:\+(?P<build>[0-9a-zA-Z_.-]+))?"
spec_version_regex_nogroups = re.sub(r"\?P<[^>]+>", "?:", spec_version_regex)


#main part of versions are compared directly
#not having prerelease > having one
#build doesn't affect comparisons?

def valid(version):
    try:
        Version(version)
    except ValueError:
        return False
    return True

def clean(version):
    return str(Version(version))

def satisfies(version, spec):
    try:
        return Spec(spec).test(version)
    except ValueError:
        return False

def lt(a, b):
    return Version(a) < Version(b)

def le(a, b):
    return Version(a) <= Version(b)

def eq(a, b):
    return Version(a) == Version(b)

def ne(a, b):
    return Version(a) != Version(b)

def gt(a, b):
    return Version(a) > Version(b)

def ge(a, b):
    return Version(a) >= Version(b)

def inc(version, part):
    try:
        version = Version(version)
    except ValueError:
        return None

    if part == "major":
        version.major += 1
        version.minor = 0
        version.patch = 0
        version.prerelease = None
    elif part == "minor":
        version.minor += 1
        version.patch = 0
        version.prerelease = None
    elif part == "patch":
        version.patch += 1
        version.prerelease = None
    elif part == "prerelease":
        if version.prerelease is None:
            version.prerelease = [0]
        else:
            incremented = False
            for i in range(len(version.prerelease)):
                idx = len(version.prerelease) - 1 - i
                if type(version.prerelease[idx]) == type(0):
                    version.prerelease[idx] += 1
                    incremented = True
                    break
            if not incremented:
                version.prerelease.append(0)
    else:
        return None
    return str(version)

def validSpec(spec):
    return Spec(spec).spec

class Version(object):
    def __init__(self, version):
        self.parse(version)

    def parse(self, version):

        match = re.match(version_regex, version)
        if match is None:
            raise ValueError("Invalid version string: %s" % version)
        else:
            self.major = int(match.group("major"))
            self.minor = int(match.group("minor"))
            self.patch = int(match.group("patch"))
            self.build = match.group("build")

            prerelease = match.group("prerelease")

            if prerelease is not None:
                self.prerelease = []
                #Split prerelease into components
                prerelease = re.split("[.-]", prerelease)
                #Turn prerelease integer components into ints
                for component in prerelease:
                    if re.match(r"^[0-9]+$", component) is not None:
                        self.prerelease.append(int(component))
                    else:
                        self.prerelease.append(component)
            else:
                self.prerelease = None

    def __str__(self):
        pre = ""
        build = ""
        if self.prerelease is not None:
            pre = "-" + ".".join([str(part) for part in self.prerelease])
        if self.build is not None:
            build = "+" + self.build
        return "%d.%d.%d" % (self.major, self.minor, self.patch) + pre + build

    def __cmp__(self, other):
        if not isinstance(other, self.__class__):
            return NotImplemented

        pairs = zip([self.major, self.minor, self.patch], [other.major, other.minor, other.patch])

        for a, b in pairs:
            #If part of the version is simply missing, the one that isn't missing it has precedence.
            if a is None and b is not None:
                return -1
            elif a is not None and b is None:
                return 1
            elif a > b:
                return 1
            elif a == b:
                continue
            elif a < b:
                return -1

        #print(self.prerelease, other.prerelease)
        if self.prerelease is None and other.prerelease is not None:
            #print("Returning gt")
            return 1
        elif self.prerelease is not None and other.prerelease is None:
            return -1
        elif self.prerelease is not None and other.prerelease is not None:
            if self.prerelease == other.prerelease:
                return 0
            if len(self.prerelease) > len(other.prerelease):
                return 1
            if len(self.prerelease) < len(other.prerelease):
                return -1

            for a, b in zip(self.prerelease, other.prerelease):
                if a == b:
                    continue
                if type(a) != type(b):
                    if type(a) == str:
                        return 1
                    elif type(b) == str:
                        return -1
                elif a < b:
                    return -1
                elif a > b:
                    return 1

        return 0

    def __lt__(self, other):
        #print("lt", str(self), str(other))
        if not isinstance(other, self.__class__):
            return NotImplemented
        return self.__cmp__(other) < 0

    def __le__(self, other):
        #print("le", str(self), str(other))
        if not isinstance(other, self.__class__):
            return NotImplemented
        return self.__cmp__(other) <= 0

    def __eq__(self, other):
        #print("eq", str(self), str(other))
        if not isinstance(other, self.__class__):
            return NotImplemented
        return self.__cmp__(other) == 0

    def __ne__(self, other):
        #print("ne", str(self), str(other))
        if not isinstance(other, self.__class__):
            return NotImplemented
        return self.__cmp__(other) != 0

    def __gt__(self, other):
        #print("gt", str(self), str(other))
        if not isinstance(other, self.__class__):
            return NotImplemented
        return self.__cmp__(other) > 0

    def __ge__(self, other):
        #print("ge", str(self), str(other))
        if not isinstance(other, self.__class__):
            return NotImplemented
        return self.__cmp__(other) >= 0

"""Valid specs include:
1.2.3 : a specific version
>1.2.3 : greater than a version
<1.2.3 : less than a version
>=1.2.3 : geq than a version (a prerelease of 1.2.3 will not satisfy this!)
<=1.2.3 : leq than a version (a prerelease will satisfy this!)
1.2.3 - 2.3.4 : >=1.2.3 <=2.3.4 (range, inclusive)
~1.2.3 : >=1.2.3-0 <1.3.0-0 "reasonably close"; anything from the version supplied up to the next minor release (including prereleases of this version)
^1.2.3 : >=1.2.3-0 <2.0.0-0 "compatible with 1.2.3"; anything from the version supplied up to the next major release (including prereleases of this version)
^0.1.3 : >=0.1.3-0 <0.2.0-0 "compatible with 0.1.3"; 0.x.x versions are special in that minor changes are assumed to be API-breaking; this is like ~0.1.3
~1.2 : any version starting with 1.2
^1.2 : any version compatible with 1.2
1.2.x : any version starting with 1.2
~1 : any version starting with 1
^1 : any version compatible with 1
1.x : any version starting with 1
latest : latest version, transformed to *

spaces imply "and", and || is "or"
"""

lone_tilde = r"(?:~>?)"
lone_carat = r"(?:\^)"
lone_cmp = r"(?P<cmp>(?:<=)|(?:<)|(?:>=)|(?:>)|(?:==?)|(?:!=?)|(?:=))"
tilde_regex = lone_tilde + spec_version_regex
carat_regex = lone_carat + spec_version_regex
cmp_regex = lone_cmp + spec_version_regex
range_regex = "(?P<spec_a>" + spec_version_regex_nogroups + r")\s+-\s+(?P<spec_b>" + spec_version_regex_nogroups + ")"
x_regex = lone_cmp + "?" + spec_version_regex
requirement_regex = lone_cmp + "?(?P<version>" + version_regex + ")"

strip_regex = "(?P<operator>%s|%s|%s)\\s+(?P<spec>%s)" % (lone_tilde, lone_carat, lone_cmp, spec_version_regex)

class Requirement(object):
    def __init__(self, requirement):
        if requirement == '':
            requirement = '*'

        if requirement == '*':
            self.operator = None
            self.version = '*'
        else:
            match = re.match(requirement_regex, requirement)
            if match is None:
                raise ValueError("Invalid requirement string:", requirement)

            self.operator = match.group("cmp")
            self.version = Version(match.group("version"))

            # <1.2.3 does NOT allow 1.2.3-beta,
            # even though `1.2.3-beta < 1.2.3`
            # The assumption is that the 1.2.3 version has something you
            # *don't* want, so we push the prerelease down to the minimum.
            if self.operator == "<" and self.version.prerelease is None:
                self.version.prerelease = [0]

    def __str__(self):
        if self.operator is None:
            return str(self.version)
        else:
            return self.operator + str(self.version)

    def test(self, version):
        if self.version == '*':
            return True

        if type(version) == str:
            version = Version(version)

        if self.operator == "=" or self.operator == "==" or self.operator is None:
            return version == self.version
        if self.operator == ">":
            return version > self.version
        if self.operator == ">=":
            return version >= self.version
        if self.operator == "<":
            return version < self.version
        if self.operator == "<=":
            return version <= self.version
        if self.operator == "!=" or self.operator == "!":
            return version != self.version


class Spec(object):
    def __init__(self, specification):
        self.sets = []
        #print("Reducing", specification)

        if specification == "latest":
            specification = "*"

        for s in specification.split("||"):
            spec = s.strip(" ")
            spec = Spec.strip(spec)
            #print("spec", spec)
            spec = Spec.replaceRanges(spec)
            #print("spec", spec)
            spec = Spec.replaceTildes(spec)
            #print("spec", spec)
            spec = Spec.replaceCarats(spec)
            #print("spec", spec)
            spec = Spec.replaceXRanges(spec)
            #print("spec", spec)
            requirements = [Requirement(r) for r in re.split(r"\s+", spec)]

            self.sets.append(requirements)

        #print("Reduced", specification, "to", str(self))

    def __str__(self):
        return "||".join([" ".join([str(requirement) for requirement in s]) for s in self.sets])

    @property
    def spec(self):
        return self.__str__()

    def test(self, version):
        if type(version) == str:
            version = Version(version)

        for s in self.sets:
            passed = True
            for requirement in s:
                if not requirement.test(version):
                    passed = False
                    break
            if passed:
                return True
        return False

    @classmethod
    def isX(cls, part):
        return part == 'x' or part == 'X' or part == "*" or part is None

    @classmethod
    def strip(cls, spec):
        return re.sub(strip_regex, "\g<operator>\g<spec>", spec)

    # ~, ~> --> *
    # ~2, ~2.x, ~2.x.x, ~>2, ~>2.x ~>2.x.x --> >=2.0.0 <3.0.0
    # ~2.0, ~2.0.x, ~>2.0, ~>2.0.x --> >=2.0.0 <2.1.0
    # ~1.2, ~1.2.x, ~>1.2, ~>1.2.x --> >=1.2.0 <1.3.0
    # ~1.2.3, ~>1.2.3 --> >=1.2.3 <1.3.0
    # ~1.2.0, ~>1.2.0 --> >=1.2.0 <1.3.0
    @classmethod
    def replaceTildes(cls, spec):
        return re.sub(tilde_regex, Spec.replaceTilde, spec)

    @classmethod
    def replaceTilde(cls, match):
        major = match.group("major")
        minor = match.group("minor")
        patch = match.group("patch")
        pre = match.group("prerelease")

        #print("Replacing tilde for", match.group(0))

        #Anything
        if cls.isX(major):
            return "*"
        #From this version to the next major version
        elif cls.isX(minor):
            major = int(major)
            return ">=%d.0.0-0 <%d.0.0-0" % (major, major + 1)
        #From this version to the next minor version
        elif cls.isX(patch):
            major = int(major)
            minor = int(minor)
            patch = 0
            
            return ">=%d.%d.%d-0 <%d.%d.0-0" % (major, minor, patch, major, minor + 1)
        elif pre:
            major = int(major)
            minor = int(minor)
            patch = int(patch)

            return ">=%d.%d.%d-%s <%d.%d.0-0" % (major, minor, patch, pre, major, minor + 1)
        else:
            major = int(major)
            minor = int(minor)
            patch = int(patch)

            return ">=%d.%d.%d-0 <%d.%d.0-0" % (major, minor, patch, major, minor + 1)


    # ^ --> *
    # ^2, ^2.x, ^2.x.x --> >=2.0.0 <3.0.0
    # ^2.0, ^2.0.x --> >=2.0.0 <3.0.0
    # ^1.2, ^1.2.x --> >=1.2.0 <2.0.0
    # ^1.2.3 --> >=1.2.3 <2.0.0
    # ^1.2.0 --> >=1.2.0 <2.0.0
    @classmethod
    def replaceCarats(cls, spec):
        return re.sub(carat_regex, Spec.replaceCarat, spec)

    @classmethod
    def replaceCarat(cls, match):
        major = match.group("major")
        minor = match.group("minor")
        patch = match.group("patch")
        pre = match.group("prerelease")

        #Anything
        if cls.isX(major):
            return ""
        elif cls.isX(minor):
            major = int(major)
            return ">=%d.0.0-0 <%d.0.0-0" % (major, major + 1)
        elif cls.isX(patch):
            major = int(major)
            minor = int(minor)

            if major == 0:
                return ">=%d.%d.0-0 <%d.%d.0-0" % (major, minor, major, minor + 1)
            else:
                return ">=%d.%d.0-0 <%d.0.0-0" % (major, minor, major + 1)
        elif pre is not None:
            major = int(major)
            minor = int(minor)
            patch = int(patch)

            if major == 0:
                if minor == 0:
                    return "=%d.%d.%d-%s" % (major, minor, patch, pre)
                else:
                    return ">=%d.%d.%d-%s <%d.%d.0-0" % (major, minor, patch, pre, major, minor + 1)
            else:
                return ">=%d.%d.%d-%s <%d.0.0-0" % (major, minor, patch, pre, major + 1)
        else:
            major = int(major)
            minor = int(minor)
            patch = int(patch)

            if major == 0:
                if minor == 0:
                    return "=%d.%d.%d" % (major, minor, patch)
                else:
                    return ">=%d.%d.%d-0 <%d.%d.0-0" % (major, minor, patch, major, minor + 1)
            else:
                return ">=%d.%d.%d-0 <%d.0.0-0" % (major, minor, patch, major + 1)

    @classmethod
    def replaceXRanges(cls, spec):
        return re.sub(x_regex, Spec.replaceXRange, spec)

    @classmethod
    def replaceXRange(cls, match):
        operator = match.group("cmp")
        major = match.group("major")
        minor = match.group("minor")
        patch = match.group("patch")

        #Don't do anything if there aren't any X's in the version
        if not cls.isX(major) and not cls.isX(minor) and not cls.isX(patch):
            return match.group(0)

        if operator == "=":
            operator = None

        if operator is not None:
            if operator == ">":
                # >1 => >=2.0.0-0
                # >1.2 => >=1.3.0-0
                # >1.2.3 => >= 1.2.4-0
                operator = ">="
                if cls.isX(major):
                    major = 0
                    minor = 0
                    patch = 0
                elif cls.isX(minor):
                    major = int(major) + 1
                    minor = 0
                    patch = 0
                elif cls.isX(patch):
                    major = int(major)
                    minor = int(minor) + 1
                    patch = 0
            else:
                if cls.isX(major):
                    major = 0
                    minor = 0
                    patch = 0
                elif cls.isX(minor):
                    major = int(major)
                    minor = 0
                    patch = 0
                elif cls.isX(patch):
                    major = int(major)
                    minor = int(minor)
                    patch = 0

            ret = "%s%d.%d.%d-0" % (operator, major, minor, patch)
        elif cls.isX(major):
            return "*"
        elif cls.isX(minor):
            major = int(major)
            ret = ">=%d.0.0-0 <%d.0.0-0" % (major, major + 1)
        elif cls.isX(patch):
            major = int(major)
            minor = int(minor)
            ret = ">=%d.%d.0-0 <%d.%d.0-0" % (major, minor, major, minor + 1) 

        return ret

    # 1.2 - 3.4.5 => >=1.2.0-0 <=3.4.5
    # 1.2.3 - 3.4 => >=1.2.0-0 <3.5.0-0 Any 3.4.x will do
    # 1.2 - 3.4 => >=1.2.0-0 <3.5.0-0
    @classmethod
    def replaceRanges(cls, spec):
        return re.sub(range_regex, Spec.replaceRange, spec)

    @classmethod
    def replaceRange(cls, match):
        spec_a = match.group("spec_a")
        spec_b = match.group("spec_b")

        match = re.match(spec_version_regex, spec_a)
        major = match.group("major")
        minor = match.group("minor")
        patch = match.group("patch")
        pre = match.group("prerelease")

        if cls.isX(major):
            major = 0
            minor = 0
            patch = 0
            from_spec = ""
        elif cls.isX(minor):
            major = int(major)
            minor = 0
            patch = 0
            from_spec = ">=%d.%d.%d-0" % (major, minor, patch)
        elif cls.isX(patch):
            major = int(major)
            minor = int(minor)
            patch = 0
            from_spec = ">=%d.%d.%d-0" % (major, minor, patch)
        elif pre is not None:
            major = int(major)
            minor = int(minor)
            patch = int(patch)
            from_spec = ">=%d.%d.%d-%s" % (major, minor, pre)
        else:
            major = int(major)
            minor = int(minor)
            patch = int(patch)
            from_spec = ">=%d.%d.%d" % (major, minor, patch)

        match = re.match(spec_version_regex, spec_b)
        major = match.group("major")
        minor = match.group("minor")
        patch = match.group("patch")
        pre = match.group("prerelease")

        if cls.isX(major):
            major = 0
            minor = 0
            patch = 0
            to_spec = ""
        elif cls.isX(minor):
            major = int(major)
            minor = 0
            patch = 0
            to_spec = "<%d.%d.%d-0" % (major, minor, patch)
        elif cls.isX(patch):
            major = int(major)
            minor = int(minor)
            patch = 0
            to_spec = "<%d.%d.%d-0" % (major, minor, patch)
        elif pre is not None:
            major = int(major)
            minor = int(minor)
            patch = int(patch)
            to_spec = "<=%d.%d.%d-%s" % (major, minor, pre)
        else:
            major = int(major)
            minor = int(minor)
            patch = int(patch)
            to_spec = "<=%d.%d.%d" % (major, minor, patch)

        return from_spec + " " + to_spec




