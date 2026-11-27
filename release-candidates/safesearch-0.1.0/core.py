"""Pure, narrow AF3 3.5.11 search patch and native TMDb search command."""
from urllib.parse import urlencode
from xml.etree import ElementTree as ET

SKIN_ID = 'skin.arctic.fuse.3'
SKIN_VERSION = '3.5.11'
ADDON_ID = 'script.tvstreaming.safesearch'
ORIGINAL = ('RunScript(script.skinvariables,run_multisearch,tmdbhelper_container,'
            'progress_dialog$VAR[Value_MultiSearch_Layout_Param]'
            '$VAR[Value_MultiSearch_Discover_Param])')
VARIABLE = 'Value_TVStreaming_CrickySafeSearch'
TARGET = '$VAR[' + VARIABLE + ']'
INCLUDE = 'Home_ControlList_Item_MultiSearch'
NATIVE = 'RunScript(' + ADDON_ID + ',search)'
PROFILE_CONDITION = 'String.IsEqual(System.ProfileName,Cricky)'
MARKER = ('    <include name="' + INCLUDE + '">').encode('ascii')
OLD_LINE = ('            <param name="action">' + ORIGINAL + '</param>').encode('ascii')
NEW_LINE = ('            <param name="action">' + TARGET + '</param>').encode('ascii')


def validate(raw, patched=False):
    try:
        tree = ET.fromstring(raw)
    except ET.ParseError as exc:
        raise ValueError('Malformed skin XML; refusing to edit.') from exc
    if tree.tag != 'includes':
        raise ValueError('Unexpected Includes_Home.xml root.')
    includes = [x for x in tree.findall('include') if x.get('name') == INCLUDE]
    if len(includes) != 1:
        raise ValueError('Expected exactly one named Search include.')
    actions = includes[0].findall('./include/param[@name="action"]')
    if len(actions) != 1 or actions[0].text != (TARGET if patched else ORIGINAL):
        raise ValueError('Search action differs from the supported AF3 version.')
    variables = [v for v in tree.findall('variable') if v.get('name') == VARIABLE]
    if not patched:
        if variables:
            raise ValueError('Existing Safe Search variable found.')
        return
    if len(variables) != 1:
        raise ValueError('Expected exactly one profile-scoped Search variable.')
    values = variables[0].findall('value')
    if (len(values) != 2 or values[0].get('condition') != PROFILE_CONDITION
            or values[0].text != NATIVE or values[1].attrib
            or values[1].text != ORIGINAL):
        raise ValueError('Search profile routing did not verify.')


def patch(raw):
    validate(raw)
    if raw.count(MARKER) != 1 or raw.count(OLD_LINE) != 1:
        raise ValueError('Exact Search target is not unique; refusing to edit.')
    # Preserve original bytes, line endings and all non-Search includes.
    nl = b'\r\n' if b'\r\n' in raw else b'\n'
    variable = nl.join([
        ('    <variable name="' + VARIABLE + '">').encode('ascii'),
        ('        <value condition="' + PROFILE_CONDITION + '">' + NATIVE + '</value>').encode('ascii'),
        ('        <value>' + ORIGINAL + '</value>').encode('ascii'),
        b'    </variable>',
        b'',
        MARKER,
    ])
    changed = raw.replace(MARKER, variable, 1).replace(OLD_LINE, NEW_LINE, 1)
    validate(changed, patched=True)
    return changed


def search_command(query):
    query = query.strip()
    if not query:
        return None
    params = urlencode({'info': 'search', 'tmdb_type': 'both', 'query': query})
    return 'ActivateWindow(Videos,plugin://plugin.video.themoviedb.helper/?' + params + ',return)'
