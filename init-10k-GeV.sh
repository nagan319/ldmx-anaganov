#!/bin/bash

start_group Produce Dark Brem Library
denv init --over ldmx/dark-brem-lib-gen:v5.2.0
denv dark-brem-lib-gen \
  --run 1 \
  --nevents 10000 \
  --max-energy 8.0 \
  --apmass 1
# cleanup denv
rm -r .denv
end_group
