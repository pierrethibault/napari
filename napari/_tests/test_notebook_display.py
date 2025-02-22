import numpy as np
import pytest

from napari.utils import nbscreenshot


@pytest.mark.parametrize(
    "alt_text_input, expected_alt_text",
    [
        (None, None),
        ("Good alt text", "Good alt text"),
        # Naughty strings https://github.com/minimaxir/big-list-of-naughty-strings
        # ASCII punctuation
        (
            r",./;'[]\-=",
            ',./;&#x27;[]\\-=',
        ),  # noqa: W605
        ('<>?:"{}|_+', '&lt;&gt;?:&quot;{}|_+'),  # ASCII punctuation 2
        ("!@#$%^&*()`~", '!@#$%^&amp;*()`~'),  # ASCII punctuation 3
        # # Emjoi
        ("😍", "😍"),  # emoji 1
        ("👨‍🦰 👨🏿‍🦰 👨‍🦱 👨🏿‍🦱 🦹🏿‍♂️", "👨‍🦰 👨🏿‍🦰 👨‍🦱 👨🏿‍🦱 🦹🏿‍♂️"),  # emoji 2
        (r"¯\_(ツ)_/¯", '¯\\_(ツ)_/¯'),  # Japanese emoticon  # noqa: W605
        # # Special characters
        ("田中さんにあげて下さい", "田中さんにあげて下さい"),  # two-byte characters
        ("表ポあA鷗ŒéＢ逍Üßªąñ丂㐀𠀀", "表ポあA鷗ŒéＢ逍Üßªąñ丂㐀𠀀"),  # special unicode chars
        ("گچپژ", "گچپژ"),  # Persian special characters
        # # Script injection
        ("<script>alert(0)</script>", None),  # script injection 1
        ("&lt;script&gt;alert(&#39;1&#39;);&lt;/script&gt;", None),
        ("<svg><script>123<1>alert(3)</script>", None),
        ("<sc<script>ript>alert(13)</sc</script>ript>", None),
    ],
)
def test_nbscreenshot(make_napari_viewer, alt_text_input, expected_alt_text):
    """Test taking a screenshot."""
    viewer = make_napari_viewer()

    np.random.seed(0)
    data = np.random.random((10, 15))
    viewer.add_image(data)

    rich_display_object = nbscreenshot(viewer, alt_text=alt_text_input)
    assert hasattr(rich_display_object, '_repr_png_')
    # Trigger method that would run in jupyter notebook cell automatically
    rich_display_object._repr_png_()
    assert rich_display_object.image is not None

    html_output = rich_display_object._repr_html_()

    if expected_alt_text is None:
        assert 'alt_text=' not in html_output
    else:
        expected_output = 'alt="' + str(expected_alt_text) + '"'
        assert expected_output in html_output
