find . -type d -exec chmod go+rx {} +
find . -type f -exec chmod go+r {} +
find . -name *.cgi -exec chmod a+rx {} +
