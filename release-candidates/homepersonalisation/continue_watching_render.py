"""Candidate renderer; not connected to production widget."""
from continue_watching_feed import dismissal_key

def render(record, gui, plugin, handle, dismiss_command):
    path = record.get('file')
    if not isinstance(path, str) or not path:
        raise ValueError('Missing native callback')
    item = gui.ListItem(label=record.get('label') or record.get('title') or '', path=path)
    art = record.get('art')
    if isinstance(art, dict):
        item.setArt(art)
    info = {k: record[k] for k in ('title','plot','year','rating','playcount','season','episode','mediatype') if record.get(k) is not None}
    key = dismissal_key(record)
    if key and not info.get('mediatype'):
        info['mediatype'] = 'movie' if key.startswith('movie:') else ('episode' if record.get('episode', -1) >= 0 else 'tvshow')
    if record.get('showtitle'):
        info['tvshowtitle'] = record['showtitle']
    item.setInfo('video', info)
    tag = item.getVideoInfoTag()
    ids = record.get('uniqueid')
    if isinstance(ids, dict) and ids:
        tag.setUniqueIDs({str(k):str(v) for k,v in ids.items() if v})
    resume = record.get('resume')
    if isinstance(resume, dict):
        position, total = resume.get('position'), resume.get('total')
        if isinstance(position,(int,float)) and isinstance(total,(int,float)) and 0 <= position <= total and total > 0:
            tag.setResumePoint(float(position), float(total))
            item.setProperty('ResumeTime', str(position))
            item.setProperty('TotalTime', str(total))
    folder = record.get('filetype') != 'file'
    if not folder:
        item.setProperty('IsPlayable', 'true')
    key = dismissal_key(record)
    if key:
        item.addContextMenuItems([('Remove from Continue Watching', dismiss_command(key))])
    plugin.addDirectoryItem(handle, path, item, isFolder=folder)
    return item
