#!/usr/bin/env python

__all__ = ['miaopai_download']

from ..common import *
import urllib.error
import urllib.parse
import ssl

fake_headers_mobile = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Charset': 'UTF-8,*;q=0.5',
    'Accept-Encoding': 'gzip,deflate,sdch',
    'Accept-Language': 'en-US,en;q=0.8',
    'Referer': 'http://weibo.com',
    'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 9_1 like Mac OS X) AppleWebKit/601.1.46 (KHTML, like Gecko) Version/9.0 Mobile/13B143 Safari/601.1'
}


def miaopai_download_by_fid(fid, output_dir='.', merge=False, info_only=False, **kwargs):
    '''Source: Android mobile'''
    page_url = 'http://video.weibo.com/show?fid=' + fid + '&type=mp4'

    mobile_page = get_content(page_url, headers=fake_headers_mobile)
    url = match1(mobile_page, r'<video id=.*?src=[\'"](.*?)[\'"]\W')
    title = match1(mobile_page, r'<title>((.|\n)+?)</title>')
    if not title:
        title = fid
    title = title.replace('\n', '_')
    ext, size = 'mp4', url_info(url)[2]
    print_info(site_info, title, ext, size)
    if not info_only:
        download_urls([url], title, ext, total_size=None, output_dir=output_dir, merge=merge)


def miaopai_download_by_stream_url(url, title, output_dir='.', merge=False, info_only=False, **kwargs):
    ext, size = 'mp4', url_info(url)[2]
    print_info(site_info, title, ext, size)
    if not info_only:
        download_urls([url], title, ext, total_size=None, output_dir=output_dir, merge=merge)


# ----------------------------------------------------------------------
def miaopai_download(url, output_dir='.', merge=False, info_only=False, **kwargs):
    ssl_context = request.HTTPSHandler(
        context=ssl.SSLContext(ssl.PROTOCOL_TLSv1))
    cookie_handler = request.HTTPCookieProcessor()
    opener = request.build_opener(ssl_context, cookie_handler)
    request.install_opener(opener)
    weibo_content = get_content(url, headers=fake_headers_mobile)
    stream_url = re.search(r'"stream_url":\s*"(.*?)"', weibo_content).group(1)
    if stream_url is not None:
        print('stream_url: '+stream_url)

        page_title = re.search(r'"page_title":\s*"(.*?)"', weibo_content).group(1)
        print('page_title: ' + page_title)
        miaopai_download_by_stream_url(stream_url, page_title, output_dir, merge, info_only)
    else:
        fid = match1(url, r'\?fid=(\d{4}:\w{32})')
        if fid is not None:
            miaopai_download_by_fid(fid, output_dir, merge, info_only)
        elif '/p/230444' in url:
            fid = match1(url, r'/p/230444(\w+)')
            miaopai_download_by_fid('1034:' + fid, output_dir, merge, info_only)
        else:
            mobile_page = get_content(url, headers=fake_headers_mobile)
            hit = re.search(r'"page_url"\s*:\s*"([^"]+)"', mobile_page)
            if not hit:
                raise Exception('Unknown pattern')
            else:
                escaped_url = hit.group(1)
                miaopai_download(urllib.parse.unquote(escaped_url), output_dir=output_dir, merge=merge,
                                 info_only=info_only, **kwargs)


site_info = "miaopai"
download = miaopai_download
download_playlist = playlist_not_supported('miaopai')
