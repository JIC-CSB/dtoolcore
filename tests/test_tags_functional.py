"""Test the dataset tag functionality."""

import pytest

from . import tmp_dir_fixture


def test_tags_functional(tmp_dir_fixture):

    from dtoolcore import DataSetCreator, DataSet

    with DataSetCreator(name="empty-test-ds", base_uri=tmp_dir_fixture) as c:
        # Test put on proto dataset.
        c.put_tag("testing")

        uri = c.uri

    dataset = DataSet.from_uri(uri)
    assert dataset.get_tags() == ["testing"]

    dataset.put_tag("amazing")
    dataset.put_tag("stuff")
    assert dataset.get_tags() == ["amazing", "stuff", "testing"]

    c.delete_tag("stuff")
    assert dataset.get_tags() == ["amazing", "testing"]

    # Putting the same tag is idempotent.
    dataset.put_tag("amazing")
    dataset.put_tag("amazing")
    dataset.put_tag("amazing")
    assert dataset.get_tags() == ["amazing", "testing"]

    # Tags can only be strings.
    from dtoolcore import DtoolCoreValueError
    with pytest.raises(DtoolCoreValueError):
        dataset.put_tag(1)

    # Tags need to adhere to the utils.name_is_valid() rules.
    from dtoolcore import DtoolCoreInvalidNameError
    with pytest.raises(DtoolCoreInvalidNameError):
        dataset.put_tag("!invalid")

    # Deleting a non exiting tag raises.
    from dtoolcore import DtoolCoreKeyError
    with pytest.raises(DtoolCoreKeyError):
        c.delete_tag("dontexist")
