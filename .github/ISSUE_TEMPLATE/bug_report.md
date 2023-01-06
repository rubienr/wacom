---
name: Bug report
about: Create a report to help us improve
title: "[BUG] "
labels: bug
assignees: rubienr

---

<!-- 
Remove sections that do not apply. 
Don't feel too restricted by this template but stick to it as far you can.
-->

**Describe the bug**

<!-- 
A clear and concise description of what the bug is.

Example:
The configuration value input Area is applied at Stylus devices but at Touch devices.
Stylus and Touch devices do not necessarily share the same resolution.
-->

**How To Reproduce**

<!--
Explain in natural lanugage; if you like use Gherkin-alike syntax.

Example: 
1. GIVEN I use Cintiq 22HDT
1. GIVEN I checked out branch master
1. WHEN I run the script `xsetwacom.sh --configuration <yxz> --device set`
1. WHEN I use stylus the mapping is as expected
1. WHEN I use touch
1. THEN the mapping seems weird: the pointer is not placed below my finger
-->

**Expected behavior**

<!--
A clear and concise description of what you expected to happen.
Example: 
The pointer should be always below my finger where I touched the screen.
-->

**Files**

<!--
If applicable, add screenshots or logs to help explain your problem.
-->

**Versions (please complete the following information):**

<!--
Example script:
```bash
lsb_release -a
echo -en "xsetwacom: " && xsetwacom --version
xinput --version
xrandr --version
python --version 
```

Example output to post here:
```bash
Distributor ID:	Ubuntu
Description:	Ubuntu 22.10
Release:	22.10
Codename:	kinetic
xsetwacom: 1.0.0
xinput version 1.6.3
XI version on server: 2.4
xrandr program version       1.5.1
Server reports RandR version 1.6
Python 3.10.7
```
-->

**Additional context**

<!--
Add any other context about the problem here.
-->
