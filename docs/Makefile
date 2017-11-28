all:
	java -jar tools/swagger2markup-cli/build/libs/swagger2markup-cli-1.3.1.jar convert -i ../server/hapi/swagger/hagring.yaml -d generated
	asciidoc --out-file=HagringAPI.html index.adoc

clean:
	rm -rf generated HagringAPI.html

