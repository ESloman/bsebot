# CHANGELOG


## v2.12.0 (2025-05-05)

### Chores

- Add CODEOWNERS ([#686](https://github.com/ESloman/bsebot/pull/686),
  [`0b13284`](https://github.com/ESloman/bsebot/commit/0b132846ef7ea909808ad923e5283559cdb52579))

- Bump docker/build-push-action from 5 to 6 ([#672](https://github.com/ESloman/bsebot/pull/672),
  [`51c4a6e`](https://github.com/ESloman/bsebot/commit/51c4a6ef894b9fcf30ed49c007c1aef7a41a588d))

Bumps [docker/build-push-action](https://github.com/docker/build-push-action) from 5 to 6. -
  [Release notes](https://github.com/docker/build-push-action/releases) -
  [Commits](https://github.com/docker/build-push-action/compare/v5...v6)

--- updated-dependencies: - dependency-name: docker/build-push-action dependency-type:
  direct:production

update-type: version-update:semver-major ...

Signed-off-by: dependabot[bot] <support@github.com>

Co-authored-by: dependabot[bot] <49699333+dependabot[bot]@users.noreply.github.com>

- Bump docker/metadata-action from 5.5.1 to 5.7.0
  ([#685](https://github.com/ESloman/bsebot/pull/685),
  [`af66162`](https://github.com/ESloman/bsebot/commit/af66162e2ca5b4ec868e253a4048787d16633cee))

### Features

- 2025 updates
  ([`ed97afb`](https://github.com/ESloman/bsebot/commit/ed97afb7e79defd4f6747a7e557a75c3bff2458c))

* feat: 2025 updates

Begin making some updates. Start with updating all the requirement versions. Secondly, change the
  way we do testing. Remove all the old test data and we'll rely on mocks entirely. Set all failing
  tests because of this to 'xfail' and we'll fix them as we go.

* fix: fix the wordle solution

* fix: fix requirements.txt

* chore: update python version


## v2.11.2 (2024-08-04)

### Bug Fixes

- Fix for awards error ([#671](https://github.com/ESloman/bsebot/pull/671),
  [`f9e0010`](https://github.com/ESloman/bsebot/commit/f9e001044e5dfd9eed0ce903f3aa68fe47b8ff31))

### Continuous Integration

- Change base Docker image to slim ([#670](https://github.com/ESloman/bsebot/pull/670),
  [`1a1aacd`](https://github.com/ESloman/bsebot/commit/1a1aacdab130123985af7c0964383ad3ce5de6d3))


## v2.11.1 (2024-08-03)

### Bug Fixes

- Resolves a couple of minor bugs ([#668](https://github.com/ESloman/bsebot/pull/668),
  [`76a171b`](https://github.com/ESloman/bsebot/commit/76a171b91bf4f9d97a24fba42c31e7ff58dd7bca))

* don't trigger message action on deleted duplicates #639 * fix: fix wordle task startup condition


## v2.11.0 (2024-08-03)

### Bug Fixes

- Fix wordle task not working ([#665](https://github.com/ESloman/bsebot/pull/665),
  [`016555a`](https://github.com/ESloman/bsebot/commit/016555ac6c5788a8fd85735cd6de25d0c61adb6f))

- Temp fix for vc stat failure ([#667](https://github.com/ESloman/bsebot/pull/667),
  [`7364788`](https://github.com/ESloman/bsebot/commit/736478841e7824f4161757b7da5642e66508ab26))

Apply a quick fix for VC failure.

### Chores

- Bump docker/build-push-action from 5 to 6 ([#656](https://github.com/ESloman/bsebot/pull/656),
  [`76ed255`](https://github.com/ESloman/bsebot/commit/76ed255925c34baa3ce6ac83dc06ccc20c4c27e3))

- Bump pre-commit from 3.7.1 to 3.8.0 ([#662](https://github.com/ESloman/bsebot/pull/662),
  [`81fc5eb`](https://github.com/ESloman/bsebot/commit/81fc5eb59b92b3f0105d7f88ce2f18a93f26dfdb))

- Bump pymongo from 4.7.2 to 4.8.0 ([#658](https://github.com/ESloman/bsebot/pull/658),
  [`52b37dd`](https://github.com/ESloman/bsebot/commit/52b37dd446ac8dcf1192b49aa5ce384f2fe8e059))

- Bump python from 3.12.3 to 3.12.4 ([#655](https://github.com/ESloman/bsebot/pull/655),
  [`07dd135`](https://github.com/ESloman/bsebot/commit/07dd135728fba0f28f456da4b7cf0990938fd009))

- Bump requests from 2.32.2 to 2.32.3 ([#653](https://github.com/ESloman/bsebot/pull/653),
  [`a07dbce`](https://github.com/ESloman/bsebot/commit/a07dbce0e74c60afa78e5d1270b4f3f54443e212))

- Bump selenium from 4.21.0 to 4.23.1 ([#661](https://github.com/ESloman/bsebot/pull/661),
  [`08148e5`](https://github.com/ESloman/bsebot/commit/08148e5f8127f209599f929c53e8f07b505bf02d))

### Continuous Integration

- Add release workflow
  ([`389c129`](https://github.com/ESloman/bsebot/commit/389c1294bfef786bb04b065f74331623869f5430))

- Fix errors
  ([`f69fe3b`](https://github.com/ESloman/bsebot/commit/f69fe3b4ee07a335c08d9a7afcacb139a29f7073))

### Features

- Add basic info command ([#666](https://github.com/ESloman/bsebot/pull/666),
  [`caa5494`](https://github.com/ESloman/bsebot/commit/caa549411fc9e585364fba3701f3bc9f10fdef2f))


## v2.10.0 (2024-08-03)

### Bug Fixes

- Update ruff version ([#663](https://github.com/ESloman/bsebot/pull/663),
  [`8771705`](https://github.com/ESloman/bsebot/commit/8771705445dcf92f467c2b851b5dc6b74a4b88da))

### Chores

- Bump pre-commit from 3.6.2 to 3.7.1 ([#646](https://github.com/ESloman/bsebot/pull/646),
  [`ac5f140`](https://github.com/ESloman/bsebot/commit/ac5f1402c2a008294abad1855b7c21f4d872d78d))

- Bump pymongo from 4.7.0 to 4.7.2 ([#645](https://github.com/ESloman/bsebot/pull/645),
  [`77f1d72`](https://github.com/ESloman/bsebot/commit/77f1d727033046fad9997589c47b4ca012d84a93))

- Bump requests from 2.32.0 to 2.32.2 ([#649](https://github.com/ESloman/bsebot/pull/649),
  [`54f9ad5`](https://github.com/ESloman/bsebot/commit/54f9ad5720002e8cd5a7ba0c933954c7804e9175))

### Continuous Integration

- Ci tweaks ([#651](https://github.com/ESloman/bsebot/pull/651),
  [`e1bf393`](https://github.com/ESloman/bsebot/commit/e1bf393a3ec72a87e77811df9351f971c20c97c3))

### Features

- Feature trim ([#652](https://github.com/ESloman/bsebot/pull/652),
  [`e38d480`](https://github.com/ESloman/bsebot/commit/e38d480d6cfbf6e15af0c44745bd79cb7de5169e))

- Update ruff version ([#660](https://github.com/ESloman/bsebot/pull/660),
  [`40b5eb9`](https://github.com/ESloman/bsebot/commit/40b5eb9dcb302d0967cdd8f9125e0d152aa26fdd))


## v2.9.4 (2024-05-27)

### Bug Fixes

- Resolve issue with awards/stats ([#643](https://github.com/ESloman/bsebot/pull/643),
  [`6283549`](https://github.com/ESloman/bsebot/commit/62835490967740f840e18bd080bd6460cfe19f97))

Changing the message means that we actually return what we want. MongoDB behaviours weirdly when
  it's the other way around.

### Chores

- Bump pymongo from 4.6.2 to 4.7.0 ([#641](https://github.com/ESloman/bsebot/pull/641),
  [`df5b095`](https://github.com/ESloman/bsebot/commit/df5b0957cbb88fc4b54e22e544f567021f198a2b))

- Bump requests from 2.31.0 to 2.32.0 ([#648](https://github.com/ESloman/bsebot/pull/648),
  [`15a4c4f`](https://github.com/ESloman/bsebot/commit/15a4c4f54df1f696c84b1c0191fc485857659116))

- Bump selenium from 4.18.1 to 4.20.0 ([#640](https://github.com/ESloman/bsebot/pull/640),
  [`be9257a`](https://github.com/ESloman/bsebot/commit/be9257afc39f392ed7684c5f316f43c82e08a86c))

- Bump selenium from 4.20.0 to 4.21.0 ([#647](https://github.com/ESloman/bsebot/pull/647),
  [`5a5f1ed`](https://github.com/ESloman/bsebot/commit/5a5f1edefe1a7a0547b28bd4208f1125b3e8d486))

- Update ruff version ([#642](https://github.com/ESloman/bsebot/pull/642),
  [`175a562`](https://github.com/ESloman/bsebot/commit/175a562c4a33edf52543ec339b760d449bc94667))

- Update ruff version ([#650](https://github.com/ESloman/bsebot/pull/650),
  [`cecdc82`](https://github.com/ESloman/bsebot/commit/cecdc828c75011f141f4acc951e2d8a4f089116f))


## v2.9.3 (2024-04-23)

### Bug Fixes

- Tweak some salary messages ([#638](https://github.com/ESloman/bsebot/pull/638),
  [`a67862f`](https://github.com/ESloman/bsebot/commit/a67862ffa2f2c43bf69523d8f37e69f25c1a4cc6))


## v2.9.2 (2024-04-22)

### Bug Fixes

- Fix some formatting with salary messages ([#637](https://github.com/ESloman/bsebot/pull/637),
  [`af6e5d1`](https://github.com/ESloman/bsebot/commit/af6e5d1df625086c0f43df60f7952293e228cc52))

### Chores

- Update ruff version and resolve linting issues
  ([#636](https://github.com/ESloman/bsebot/pull/636),
  [`cb99fdc`](https://github.com/ESloman/bsebot/commit/cb99fdc3de53b64180fea64522ac2cfa8a583f05))


## v2.9.1 (2024-04-17)

### Bug Fixes

- Prevent errors when message is too long ([#635](https://github.com/ESloman/bsebot/pull/635),
  [`4aaf3f9`](https://github.com/ESloman/bsebot/commit/4aaf3f9d605e70b5fa2c043f00ad8c9d0b588f48))

### Chores

- Bump python from 3.12.2 to 3.12.3 ([#634](https://github.com/ESloman/bsebot/pull/634),
  [`f6cf999`](https://github.com/ESloman/bsebot/commit/f6cf99981b1e9297eab7ce975c61d102bc21fc9a))

Bumps python from 3.12.2 to 3.12.3.

--- updated-dependencies: - dependency-name: python dependency-type: direct:production

update-type: version-update:semver-patch ...

Signed-off-by: dependabot[bot] <support@github.com>

Co-authored-by: dependabot[bot] <49699333+dependabot[bot]@users.noreply.github.com>

### Testing

- #631 use orjson ([#633](https://github.com/ESloman/bsebot/pull/633),
  [`e0aeb7f`](https://github.com/ESloman/bsebot/commit/e0aeb7f3954c8c85669cbe375a650d463d7e0f15))


## v2.9.0 (2024-04-15)

### Features

- #618 improve salary message ([#632](https://github.com/ESloman/bsebot/pull/632),
  [`3e69afb`](https://github.com/ESloman/bsebot/commit/3e69afb5e7b8aab97b2d7180e58c2dc28896d331))


## v2.8.0 (2024-04-12)

### Features

- #627 track last salary time in the database ([#630](https://github.com/ESloman/bsebot/pull/630),
  [`eafb162`](https://github.com/ESloman/bsebot/commit/eafb1623c2fcda0031af03cf8ce0e32ded931e95))

### Testing

- Update pytest config ([#629](https://github.com/ESloman/bsebot/pull/629),
  [`9712cf2`](https://github.com/ESloman/bsebot/commit/9712cf2385538743fc7b83321f0e812510849b43))


## v2.7.3 (2024-04-11)

### Bug Fixes

- Resolve linting errors ([#628](https://github.com/ESloman/bsebot/pull/628),
  [`2db7fc7`](https://github.com/ESloman/bsebot/commit/2db7fc75d4a517a7355be3dd544778c8d23397f6))


## v2.7.2 (2024-04-09)

### Bug Fixes

- Resolve some sonar issues ([#624](https://github.com/ESloman/bsebot/pull/624),
  [`27ea1e9`](https://github.com/ESloman/bsebot/commit/27ea1e96db456f62ecc34d4a27553673ce9ed897))

* Replace a duplicated string with a constant * Reduce complexity of this function * Refactor to
  reduce further complexity * Switch tests to ZoneInfo * Add tests for celebrations task * Add tests
  for onmessageedit

### Continuous Integration

- Fix CI issues ([#623](https://github.com/ESloman/bsebot/pull/623),
  [`c64c7fd`](https://github.com/ESloman/bsebot/commit/c64c7fdec929dc44afc2f9bf644008576fef4447))

Ensure that we are actually checking for errors after we run the BSEBot container for a couple of
  minutes.

### Refactoring

- Update and simplify main.py ([#612](https://github.com/ESloman/bsebot/pull/612),
  [`4b538d1`](https://github.com/ESloman/bsebot/commit/4b538d1351f218d0739c080bbc98da4f0269d8c1))

Refactor and simplify main.


## v2.7.1 (2024-04-09)

### Bug Fixes

- Resolve error with edits in DM channels ([#622](https://github.com/ESloman/bsebot/pull/622),
  [`2268397`](https://github.com/ESloman/bsebot/commit/226839770f83d174fb1ec1c15e86a72ad3282db3))

### Chores

- Update dependabot config ([#621](https://github.com/ESloman/bsebot/pull/621),
  [`814b485`](https://github.com/ESloman/bsebot/commit/814b485b1c10f5025dc96b5e55c77e85c18e5387))


## v2.7.0 (2024-03-25)

### Bug Fixes

- Make sure revolution bribe task is actually triggered
  ([#608](https://github.com/ESloman/bsebot/pull/608),
  [`76711f7`](https://github.com/ESloman/bsebot/commit/76711f7bbafdcbf1e673b62dc39f7699cc200abf))

- Resolve issue with vally task triggered too many times
  ([#606](https://github.com/ESloman/bsebot/pull/606),
  [`6886fc9`](https://github.com/ESloman/bsebot/commit/6886fc9ac23840b554e78a6d72ad9a4ecbbe527f))

- Update readme to reflect new CI ([#605](https://github.com/ESloman/bsebot/pull/605),
  [`50000fe`](https://github.com/ESloman/bsebot/commit/50000fe7d34968071065dfb495c00c2329066b59))

### Continuous Integration

- Add semantic-versioning ([#611](https://github.com/ESloman/bsebot/pull/611),
  [`ff8e939`](https://github.com/ESloman/bsebot/commit/ff8e939514d69d970a144e75628733e17370130a))

add semantic release stuff

Closes #600

- Hopefully fix concurrency ([#610](https://github.com/ESloman/bsebot/pull/610),
  [`69ffced`](https://github.com/ESloman/bsebot/commit/69ffced98bfd3e841709f73e30963479e2981ea1))

- Update to use one workflow ([#604](https://github.com/ESloman/bsebot/pull/604),
  [`a6acbda`](https://github.com/ESloman/bsebot/commit/a6acbda4707dde714262a1c366eeaa2978bf23ba))

- Use deploy key for semantic-release ([#613](https://github.com/ESloman/bsebot/pull/613),
  [`fb89214`](https://github.com/ESloman/bsebot/commit/fb892148d825438199472d5b48c4b21a7f56cf73))

### Documentation

- Point readme workflow status badge at main branch
  ([#607](https://github.com/ESloman/bsebot/pull/607),
  [`24cbbb8`](https://github.com/ESloman/bsebot/commit/24cbbb8db6b5e03ce442bf01d718ad7d74b0267d))

### Features

- Add docker-compose file and ci fixes ([#615](https://github.com/ESloman/bsebot/pull/615),
  [`feeda3a`](https://github.com/ESloman/bsebot/commit/feeda3ac3b889bc804e637470246b7fae646e997))

### Refactoring

- Update to use sloman-logging package ([#603](https://github.com/ESloman/bsebot/pull/603),
  [`002f5f6`](https://github.com/ESloman/bsebot/commit/002f5f60d024fbe436dfb7968b3a76ba85755576))


## v2.6.0 (2024-03-25)
