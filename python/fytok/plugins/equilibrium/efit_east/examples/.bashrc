# .bashrc

# Source global definitions
if [ -f /etc/bashrc ]; then
	. /etc/bashrc
fi

# User specific aliases and functions
source  /gpfs/fuyun//software/lmod/lmod/init/bash
module use /gpfs/fuyun/modules/all/
module load  fytok_ext/0.0.0-foss-2022b
