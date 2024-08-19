# CHANGELOG



## v0.3.1 (2024-08-19)

### Build

* build: revise dockerfile ([`ed5d4e0`](https://gitlab.com/inteliver/inteliver/-/commit/ed5d4e07507ff9218043af1c2a2a00d6dbaadf60))


## v0.3.0 (2024-08-19)

### Build

* build: change pipeline name ([`3ddac3f`](https://gitlab.com/inteliver/inteliver/-/commit/3ddac3f63f8bb2a5d605d1f4b487942b2de5d24c))

* build: update docker image name to simply inteliver:latest ([`dc3c7b8`](https://gitlab.com/inteliver/inteliver/-/commit/dc3c7b88146689afaf7278478312befeafa69eae))

* build: update numpy version to be compatible with opencv ([`1e6cff1`](https://gitlab.com/inteliver/inteliver/-/commit/1e6cff1ebeda2b29519d8eb8dfbdeed4bcbcb8a4))

* build: add requirements to pyproject.tom ([`9ac38c1`](https://gitlab.com/inteliver/inteliver/-/commit/9ac38c1957268351ffdd475ae6d6185582c3791e))

* build: change package name to simply inteliver ([`6b7fe01`](https://gitlab.com/inteliver/inteliver/-/commit/6b7fe01c0eb3bdf62516fa167ace194ea7a27ac3))

* build: update dockerfile ([`9c66447`](https://gitlab.com/inteliver/inteliver/-/commit/9c664475de2ce42f05dd09451478e955a8f01d03))

* build: add local dev mode with docker compose ([`3906ff4`](https://gitlab.com/inteliver/inteliver/-/commit/3906ff45ec07cf8346838e122dbd7bd3fba61202))

* build: ignore ai model files ([`7bd434e`](https://gitlab.com/inteliver/inteliver/-/commit/7bd434e4e1e76f5490f2380bdc076782ab995d18))

* build: ignore vscode and logs ([`82f1e92`](https://gitlab.com/inteliver/inteliver/-/commit/82f1e92b12d827295648929f2dc69fd174c72e97))

* build: add pyjwt ([`13eadbc`](https://gitlab.com/inteliver/inteliver/-/commit/13eadbc357d9b13891dacce52c2f1e03d45990e8))

* build: ignore pdoc ([`566234a`](https://gitlab.com/inteliver/inteliver/-/commit/566234a5d5f24c476a5900c0fb5bcf72a3309237))

* build: add postgres to docker compose ([`f4e0fbe`](https://gitlab.com/inteliver/inteliver/-/commit/f4e0fbeb28fc461956bb8b87e04577d8dbf25016))

### Documentation

* docs: add inteliver features to readme ([`cbb50a7`](https://gitlab.com/inteliver/inteliver/-/commit/cbb50a7c8dfd604e788eed94ea06bd2eff609ad6))

* docs: add inteliver logo for readme ([`8ed1ca8`](https://gitlab.com/inteliver/inteliver/-/commit/8ed1ca81b41dc6bba712df11fc8829decfa4a9da))

* docs: first draft of readme ([`af34cb6`](https://gitlab.com/inteliver/inteliver/-/commit/af34cb613368496bfb91f060e4f060d405415eb2))

* docs: add code documentation ([`9de3a67`](https://gitlab.com/inteliver/inteliver/-/commit/9de3a674101af311f4d3713f0532639cc5c12add))

### Feature

* feat: add image processing module ([`3738c9e`](https://gitlab.com/inteliver/inteliver/-/commit/3738c9e90b53de0fa73d76e54721c846bb41d162))

* feat: add object storage endpoints ([`be2dd32`](https://gitlab.com/inteliver/inteliver/-/commit/be2dd32f49d479b639b618b5406cd7e54d98f7d9))

* feat: add register flow ([`7da0363`](https://gitlab.com/inteliver/inteliver/-/commit/7da036371864318bbbc43c7b19d9f16947b61ad2))

* feat: add reset password and other improvements ([`94967b2`](https://gitlab.com/inteliver/inteliver/-/commit/94967b295a37a31e8e2f9d4086986b9088d5ebd3))

* feat: add auth to user routers ([`9c45980`](https://gitlab.com/inteliver/inteliver/-/commit/9c459801b1e494b60add3d441161c62b3c5596a2))

* feat: add auth using oauth2 ([`d21de7f`](https://gitlab.com/inteliver/inteliver/-/commit/d21de7fb429bcdc84241a72e2b7182835143b309))

* feat: add user endpoints ([`b57f423`](https://gitlab.com/inteliver/inteliver/-/commit/b57f423ba932d9d43648008bed5a4f7b8d07333f))

* feat: add postgres database and alembic migrations ([`fa19fa2`](https://gitlab.com/inteliver/inteliver/-/commit/fa19fa27a46e5a851856654fb317d934ff0fdd94))

* feat: add users schema, model and crud ([`f605b98`](https://gitlab.com/inteliver/inteliver/-/commit/f605b98a13668dfe0c344fcd197a40bcff88d03a))

### Fix

* fix: ruff and my issues ([`708348a`](https://gitlab.com/inteliver/inteliver/-/commit/708348aa9e237845e00d4d620fc60d341c93ff9c))

* fix: add exception handling for initializing the database ([`26964f8`](https://gitlab.com/inteliver/inteliver/-/commit/26964f81e1d909c4364eeada9ebc018a1bfdc354))

* fix: change variable name ([`1804ef9`](https://gitlab.com/inteliver/inteliver/-/commit/1804ef921f6a1579a4e3e6e5a25975d077f17e92))

* fix: change default error message ([`6380d9c`](https://gitlab.com/inteliver/inteliver/-/commit/6380d9cfc70bc9f4413013cab7d0bdce6652dfda))

* fix: use default loguru logger with added outputs ([`8e7dc36`](https://gitlab.com/inteliver/inteliver/-/commit/8e7dc360279d3aaed5a3b5cb12021e09ef1790b1))

* fix: read cloudname from database ([`46b1d76`](https://gitlab.com/inteliver/inteliver/-/commit/46b1d7660d829515791c2849fb2253d049357278))

* fix: add storage to routers ([`53ca2ab`](https://gitlab.com/inteliver/inteliver/-/commit/53ca2ab724a34dabb7a33ef738d062250449b08b))

* fix: update cli project name ([`2af8ef4`](https://gitlab.com/inteliver/inteliver/-/commit/2af8ef4693514a1924c29399cee8e86e3d273d48))

* fix: remove code pdoc ([`4f333d7`](https://gitlab.com/inteliver/inteliver/-/commit/4f333d7435bc0f7f1584fb5f58b1f3f23bcff0c1))

* fix: resolve the unknown revision error in ci ([`089a7a5`](https://gitlab.com/inteliver/inteliver/-/commit/089a7a5010892565f7273b38d28515e03c2ed1a8))

### Refactor

* refactor: aggregate all configs ([`a390c66`](https://gitlab.com/inteliver/inteliver/-/commit/a390c666bc2466900749f940193b3b8e8a0ab2db))

* refactor: add cloudname functionality and other fixes ([`94975e8`](https://gitlab.com/inteliver/inteliver/-/commit/94975e880eacdc8e249a6404d67675528ec3fced))

* refactor: revision new alembic migration ([`ab2fc10`](https://gitlab.com/inteliver/inteliver/-/commit/ab2fc10bb96d3c62643581c69a0b6f1566d8b47e))

* refactor: move versioning to its module ([`58826db`](https://gitlab.com/inteliver/inteliver/-/commit/58826dbddc36635f4011122eab2688aedc2bab78))

* refactor: remove unused folders ([`63e5401`](https://gitlab.com/inteliver/inteliver/-/commit/63e54011e9baa12797beee43aab78bcd8da6481a))

* refactor: add constants to auth ([`dc01296`](https://gitlab.com/inteliver/inteliver/-/commit/dc012965b28f665ccbc85f0ab63ff419d9f0eaf9))

* refactor: improve auth module ([`479f538`](https://gitlab.com/inteliver/inteliver/-/commit/479f53863014bfab2558576fa0d34f5df5c96d07))

* refactor: moved postgres db ([`349f762`](https://gitlab.com/inteliver/inteliver/-/commit/349f762f0ff936317df8b8d310d5dcbff76c1a36))


## v0.2.0 (2024-07-18)

### Feature

* feat: add mkdocs ([`41ca295`](https://gitlab.com/inteliver/inteliver/-/commit/41ca295db66f23bded3a04adcc713b0f50edfdec))


## v0.1.4 (2024-07-17)

### Style

* style: chnage to a more cleaner docker image name ([`800841f`](https://gitlab.com/inteliver/inteliver/-/commit/800841f94be13ac3a05606583ce91f72cf30173c))


## v0.1.3 (2024-07-17)

### Fix

* fix: add make package to dockerfile ([`119496a`](https://gitlab.com/inteliver/inteliver/-/commit/119496a07de46d9ccf6a0609f0e44f7cb32843a1))


## v0.1.2 (2024-07-17)

### Fix

* fix: tried to fix yaml structure ([`c2aac19`](https://gitlab.com/inteliver/inteliver/-/commit/c2aac19a6f41605a75443af0b8b49135162242f3))


## v0.1.1 (2024-07-17)

### Build

* build: add actions for docker build and push ([`f3bc6d3`](https://gitlab.com/inteliver/inteliver/-/commit/f3bc6d3cd9eac3b988e7083bddfe70799ba7b041))

### Fix

* fix: linting issues ([`ce41094`](https://gitlab.com/inteliver/inteliver/-/commit/ce410941f3939265729c568469ac541cf29b2dd3))


## v0.1.0 (2024-07-17)

### Build

* build: update cli command ([`957ac62`](https://gitlab.com/inteliver/inteliver/-/commit/957ac62fd5ec110128f118cc86aab140d0804ea8))

* build: add typer cli ([`3cb8ef7`](https://gitlab.com/inteliver/inteliver/-/commit/3cb8ef7bd14defd386cc58bcbb3a044dbca22ce5))

### Documentation

* docs: update description and authors ([`87209a5`](https://gitlab.com/inteliver/inteliver/-/commit/87209a50feff7a4730ffb66834dee2354dea0f86))

* docs: update documentation ([`0df0818`](https://gitlab.com/inteliver/inteliver/-/commit/0df0818ad1ae3d9f625598ac2bb67d33137a1d54))

### Fix

* fix: remove unnecessary interface and gradio ([`68c3c6f`](https://gitlab.com/inteliver/inteliver/-/commit/68c3c6fdbe30e34ecba4f2f049f5d31ee013739b))

* fix: remove template changelog details ([`d38f9d3`](https://gitlab.com/inteliver/inteliver/-/commit/d38f9d3fd548e7ea560d824932492e374efaa577))

* fix: remove unnecessary features ([`5780a5a`](https://gitlab.com/inteliver/inteliver/-/commit/5780a5af44be22c3b5b67dc398fd6b1e073f0a33))

* fix: rename general variables and service name ([`9918515`](https://gitlab.com/inteliver/inteliver/-/commit/9918515c9da6ae15f438696884880c4910f46d86))

### Refactor

* refactor: separate strings into a constant file ([`1dfed02`](https://gitlab.com/inteliver/inteliver/-/commit/1dfed026ee504e275cc9ff43be9f1681b6464bc0))

### Unknown

* Initial commit ([`b7ffe2f`](https://gitlab.com/inteliver/inteliver/-/commit/b7ffe2f4bdf9287c0938085390bcd915cad1a9aa))
