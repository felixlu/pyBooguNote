pyBooguNote
===========

A simple, incomplete &amp; unofficial implement of BooguNote written in Python 3
-- for crossplatform purpose, especially on Mac and Linux.

Features:
* Read and display .boo tree node: text and icon
* Expand/collapse node
** Update "branch"
* Edit .boo tree node: text and icon, and save to file
** Update "content", "icon"
** [TODO] Update "ModifyTime"
* Add/delete child node and refresh whole tree
** Update "level", "branch", "IsShow"
** Keep the expansion state of other nodes
* [TODO] Move node up/down/left/right
** [TODO] Update tree node
** [TODO] Update "level"
* [TODO] Add sibling node before/after current node
** [TODO] Update "level"
* Compatibility
** [TODO] Add encoding and standalone attribute to document root
