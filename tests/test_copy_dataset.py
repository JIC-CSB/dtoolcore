"""Test the dtoolcore.copy function."""

import os

import pytest

from . import tmp_dir_fixture  # NOQA
from . import TEST_SAMPLE_DATA


def test_copy(tmp_dir_fixture):  # NOQA

    import dtoolcore

    src_dir = os.path.join(tmp_dir_fixture, "src")
    dest_dir = os.path.join(tmp_dir_fixture, "dest")
    for directory in [src_dir, dest_dir]:
        os.mkdir(directory)

    # Create the src dataset to be copied.
    admin_metadata = dtoolcore.generate_admin_metadata("test_copy")
    proto_dataset = dtoolcore.generate_proto_dataset(
        admin_metadata=admin_metadata,
        base_uri=src_dir
    )
    proto_dataset.create()
    src_uri = proto_dataset.uri

    proto_dataset.put_readme("---\nproject: exciting\n")

    overlay = "file_extension"
    for fname in os.listdir(TEST_SAMPLE_DATA):
        _, ext = os.path.splitext(fname)
        item_fpath = os.path.join(TEST_SAMPLE_DATA, fname)
        proto_dataset.put_item(item_fpath, fname)
        proto_dataset.add_item_metadata(fname, overlay, ext)

    proto_dataset.freeze()

    # Copy the src dataset to dest.
    dest_uri = dtoolcore.copy(src_uri, dest_dir)

    # Compare the two datasets.
    src_ds = dtoolcore.DataSet.from_uri(src_uri)
    dest_ds = dtoolcore.DataSet.from_uri(dest_uri)

    for key, value in src_ds._admin_metadata.items():
        if key == "frozen_at":
            tolerance = 2  # seconds (number chosen arbitrarily)
            assert dest_ds._admin_metadata[key] >= value
            assert dest_ds._admin_metadata[key] < value + tolerance
        else:
            assert dest_ds._admin_metadata[key] == value

    assert src_ds.identifiers == dest_ds.identifiers
    for i in src_ds.identifiers:
        src_item_props = src_ds.item_properties(i)
        dest_item_props = dest_ds.item_properties(i)
        for key, value in src_item_props.items():
            if key == "utc_timestamp":
                tolerance = 2  # seconds (number chosen arbitrarily)
                assert dest_item_props[key] >= value
                assert dest_item_props[key] < value + tolerance
            else:
                assert dest_item_props[key] == value

    assert src_ds.get_readme_content() == dest_ds.get_readme_content()

    assert src_ds.list_overlay_names() == dest_ds.list_overlay_names()
    assert src_ds.get_overlay(overlay) == dest_ds.get_overlay(overlay)


def test_copy_resume(tmp_dir_fixture):  # NOQA

    import dtoolcore

    src_dir = os.path.join(tmp_dir_fixture, "src")
    dest_dir = os.path.join(tmp_dir_fixture, "dest")
    for directory in [src_dir, dest_dir]:
        os.mkdir(directory)

    # Create the src dataset to be copied.
    admin_metadata = dtoolcore.generate_admin_metadata("test_copy")
    proto_dataset = dtoolcore.generate_proto_dataset(
        admin_metadata=admin_metadata,
        base_uri=src_dir
    )
    proto_dataset.create()
    src_uri = proto_dataset.uri

    proto_dataset.put_readme("---\nproject: exciting\n")

    overlay = "file_extension"
    for fname in os.listdir(TEST_SAMPLE_DATA):
        _, ext = os.path.splitext(fname)
        item_fpath = os.path.join(TEST_SAMPLE_DATA, fname)
        proto_dataset.put_item(item_fpath, fname)
        proto_dataset.add_item_metadata(fname, overlay, ext)

    proto_dataset.freeze()

    # Create a partial copy.
    src_dataset = dtoolcore.DataSet.from_uri(proto_dataset.uri)
    dtoolcore._copy_create_proto_dataset(
        src_dataset,
        dest_dir
    )

    # Copy should fail.
    import dtoolcore.storagebroker
    with pytest.raises(dtoolcore.storagebroker.StorageBrokerOSError):
        dest_uri = dtoolcore.copy(src_uri, dest_dir)

    # Copy resume should work.
    dest_uri = dtoolcore.copy_resume(src_uri, dest_dir)

    # Compare the two datasets.
    src_ds = dtoolcore.DataSet.from_uri(src_uri)
    dest_ds = dtoolcore.DataSet.from_uri(dest_uri)

    for key, value in src_ds._admin_metadata.items():
        if key == "frozen_at":
            tolerance = 2  # seconds (number chosen arbitrarily)
            assert dest_ds._admin_metadata[key] >= value
            assert dest_ds._admin_metadata[key] < value + tolerance
        else:
            assert dest_ds._admin_metadata[key] == value

    assert src_ds.identifiers == dest_ds.identifiers
    for i in src_ds.identifiers:
        src_item_props = src_ds.item_properties(i)
        dest_item_props = dest_ds.item_properties(i)
        for key, value in src_item_props.items():
            if key == "utc_timestamp":
                tolerance = 2  # seconds (number chosen arbitrarily)
                assert dest_item_props[key] >= value
                assert dest_item_props[key] < value + tolerance
            else:
                assert dest_item_props[key] == value

    assert src_ds.get_readme_content() == dest_ds.get_readme_content()

    assert src_ds.list_overlay_names() == dest_ds.list_overlay_names()
    assert src_ds.get_overlay(overlay) == dest_ds.get_overlay(overlay)

    # Copy resume should fail on frozen dataset.
    with pytest.raises(dtoolcore.DtoolCoreTypeError):
        dest_uri = dtoolcore.copy_resume(src_uri, dest_dir)


def test_copy_resume_fixes_broken_files(tmp_dir_fixture):  # NOQA

    import dtoolcore

    src_dir = os.path.join(tmp_dir_fixture, "src")
    dest_dir = os.path.join(tmp_dir_fixture, "dest")
    for directory in [src_dir, dest_dir]:
        os.mkdir(directory)

    # Create the src dataset to be copied.
    admin_metadata = dtoolcore.generate_admin_metadata("test_copy")
    proto_dataset = dtoolcore.generate_proto_dataset(
        admin_metadata=admin_metadata,
        base_uri=src_dir
    )
    proto_dataset.create()
    src_uri = proto_dataset.uri

    proto_dataset.put_readme("---\nproject: exciting\n")

    overlay = "file_extension"
    for fname in os.listdir(TEST_SAMPLE_DATA):
        _, ext = os.path.splitext(fname)
        item_fpath = os.path.join(TEST_SAMPLE_DATA, fname)
        proto_dataset.put_item(item_fpath, fname)
        proto_dataset.add_item_metadata(fname, overlay, ext)

    proto_dataset.freeze()

    # Create a partial copy.
    src_dataset = dtoolcore.DataSet.from_uri(proto_dataset.uri)
    dest_proto_dataset = dtoolcore._copy_create_proto_dataset(
        src_dataset,
        dest_dir
    )
    broken_content_fpath = os.path.join(TEST_SAMPLE_DATA, "another_file.txt")
    dest_proto_dataset.put_item(broken_content_fpath, "random_bytes")

    # Copy resume should work.
    dest_uri = dtoolcore.copy_resume(src_uri, dest_dir)

    # Compare the two datasets.
    src_ds = dtoolcore.DataSet.from_uri(src_uri)
    dest_ds = dtoolcore.DataSet.from_uri(dest_uri)

    for key, value in src_ds._admin_metadata.items():
        if key == "frozen_at":
            tolerance = 2  # seconds (number chosen arbitrarily)
            assert dest_ds._admin_metadata[key] >= value
            assert dest_ds._admin_metadata[key] < value + tolerance
        else:
            assert dest_ds._admin_metadata[key] == value

    assert src_ds.identifiers == dest_ds.identifiers
    for i in src_ds.identifiers:
        src_item_props = src_ds.item_properties(i)
        dest_item_props = dest_ds.item_properties(i)
        for key, value in src_item_props.items():
            if key == "utc_timestamp":
                tolerance = 2  # seconds (number chosen arbitrarily)
                assert dest_item_props[key] >= value
                assert dest_item_props[key] < value + tolerance
            else:
                assert dest_item_props[key] == value

    assert src_ds.get_readme_content() == dest_ds.get_readme_content()

    assert src_ds.list_overlay_names() == dest_ds.list_overlay_names()
    assert src_ds.get_overlay(overlay) == dest_ds.get_overlay(overlay)
