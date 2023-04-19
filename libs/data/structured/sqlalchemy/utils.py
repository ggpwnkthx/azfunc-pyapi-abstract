import re
import inflect


def camelize_classname(base, tablename, table):
    "Produce a 'camelized' class name, e.g."
    "'words_and_underscores' -> 'WordsAndUnderscores'"
    schema = table.schema.replace(" ", "_")
    schema = str(
        schema[0].upper()
        + re.sub(r"_([a-z])", lambda m: m.group(1).upper(), schema[1:])
    )
    tablename = tablename.replace(" ", "_")
    tablename = str(
        tablename[0].upper()
        + re.sub(r"_([a-z])", lambda m: m.group(1).upper(), tablename[1:])
    )
    return schema + tablename


_pluralizer = inflect.engine()


def pluralize_collection(base, local_cls, referred_cls, constraint):
    "Produce an 'uncamelized', 'pluralized' class name, e.g."
    "'SomeTerm' -> 'some_terms'"

    referred_name = referred_cls.__name__
    uncamelized = re.sub(r"[A-Z]", lambda m: "_%s" % m.group(0).lower(), referred_name)[
        1:
    ]
    pluralized = _pluralizer.plural(uncamelized)
    return pluralized

