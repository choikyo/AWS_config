for %%f in (*.jpg) do convert %%~nxf -resize 800 ..\%%~nf.jpg