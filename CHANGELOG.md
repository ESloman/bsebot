# CHANGELOG



## v2.7.0 (2024-03-25)

### Ci

* ci: use deploy key for semantic-release (#613) ([`fb89214`](https://github.com/ESloman/bsebot/commit/fb892148d825438199472d5b48c4b21a7f56cf73))

* ci: add semantic-versioning (#611)

add semantic release stuff

Closes #600 ([`ff8e939`](https://github.com/ESloman/bsebot/commit/ff8e939514d69d970a144e75628733e17370130a))

* ci: hopefully fix concurrency (#610) ([`69ffced`](https://github.com/ESloman/bsebot/commit/69ffced98bfd3e841709f73e30963479e2981ea1))

* ci: update to use one workflow (#604) ([`a6acbda`](https://github.com/ESloman/bsebot/commit/a6acbda4707dde714262a1c366eeaa2978bf23ba))

### Documentation

* docs: point readme workflow status badge at main branch (#607) ([`24cbbb8`](https://github.com/ESloman/bsebot/commit/24cbbb8db6b5e03ce442bf01d718ad7d74b0267d))

### Feature

* feat: add docker-compose file and ci fixes (#615) ([`feeda3a`](https://github.com/ESloman/bsebot/commit/feeda3ac3b889bc804e637470246b7fae646e997))

### Fix

* fix: make sure revolution bribe task is actually triggered (#608) ([`76711f7`](https://github.com/ESloman/bsebot/commit/76711f7bbafdcbf1e673b62dc39f7699cc200abf))

* fix: resolve issue with vally task triggered too many times (#606) ([`6886fc9`](https://github.com/ESloman/bsebot/commit/6886fc9ac23840b554e78a6d72ad9a4ecbbe527f))

* fix: update readme to reflect new CI (#605) ([`50000fe`](https://github.com/ESloman/bsebot/commit/50000fe7d34968071065dfb495c00c2329066b59))

### Refactor

* refactor: update to use sloman-logging package (#603) ([`002f5f6`](https://github.com/ESloman/bsebot/commit/002f5f60d024fbe436dfb7968b3a76ba85755576))

### Unknown

* refacfor: remove dependence on guild ids (#609)

Remove dependence on hard-coded guild IDs.

Closes #593 ([`a7c8b7e`](https://github.com/ESloman/bsebot/commit/a7c8b7e9475fa1e7938648ebca07b420634fe560))


## v2.6.0 (2024-03-25)

### Unknown

* #550 - Dynamic Bet Amounts (#596)

Let bet amounts be more dynamic.
Rather than hard-coding all the amounts - try and generate some that are more dynamic so that they scale with the eddies the users actually have. ([`bfa2ed9`](https://github.com/ESloman/bsebot/commit/bfa2ed911e6185bdcb0c8d06b1cab94516964946))

* #578 - Add Revolution Bribes (#595)

Add a system that allows the user to bribe the bot into reducing the chance of a revolution.
This is only offered to the user if:
- high chance of losing
- they can&#39;t afford to &#39;save thyself&#39; without losing the King title
- they haven&#39;t already saved themselves
- they haven&#39;t been King for more than a month
- they aren&#39;t in the top 2 for longest Kings

They get the choice of accepting or refusing the offer. ([`d7aa9bf`](https://github.com/ESloman/bsebot/commit/d7aa9bfb5995b3b8a297afa4bc7aa70d5a9c43b0))

* Change to public docker repo (#589)

Change to esloman repo ([`133d913`](https://github.com/ESloman/bsebot/commit/133d913501331b1aaa73bcf7f4078da1bece2467))

* Add alphabetical reactions (#587)

- update to add a message reaction for alphabetical messages
- add `alphabetical` message type and eddies award
- add tests for it
- update to ruff 0.3.4 ([`a864271`](https://github.com/ESloman/bsebot/commit/a8642714b0b8b3313bfa69a21d9b6785bfe8b8e5))

* #390 - A better task manager (#583)

Improve the task manager to actually disable/enable tasks when they&#39;re not required.

- Define a `TaskSchedule` class for defining when a task should run.
- Task Manager will check each task to see if it matches the schedule - disabling those that aren&#39;t needed and enable those that do
- Have an &#39;overriden&#39; property which allows us to trigger a task despite it&#39;s schedule
- Set schedules for each task
- Set default status of tasks to not started
- Set loop count to 1 for infrequent tasks - preventing them running accidentally multiple times ([`b247eef`](https://github.com/ESloman/bsebot/commit/b247eef28725a9c41de9626328f380f01ffbb7d0))

* Fix sonar issues (#581)

Fixes a number of sonar issues:
- replace pytz with zoneinfo
- reduce the complexity of some functions
- add some base UI classes: BSEView and BSESelect
- add some more consistency to callback names
- add some more tests
- add type hints ([`7d7e11d`](https://github.com/ESloman/bsebot/commit/7d7e11d96475cc55aa88b3e09a9dc09dbfcb1f2b))

* #579 - Remove credentials from Docker image (#580)

- Remove credentials from image
- Remove build args
- Update workflows to use environment variables for running
- Add some logging regarding flags and tokens
- Update log rotation values
- Update the `update.sh` script to mount a local `.env` and mount the logs  directory so we can persist logs too
- Update README.md ([`553194a`](https://github.com/ESloman/bsebot/commit/553194ad4003acbb3d7cfdc569368c99ab30caf1))

* Fix tests ([`be0bd7a`](https://github.com/ESloman/bsebot/commit/be0bd7ae3dcf53180bf8634d33f3b9272386ff6f))

* Wordle Fixes (#577)

* Amend the wordle regex to take into account commas
* Fix an issue with tough day ([`fc56b82`](https://github.com/ESloman/bsebot/commit/fc56b8236bc08acc87952c7981a47968cfdb5918))

* Bump pre-commit from 3.6.1 to 3.6.2 (#570) ([`aa0d3a7`](https://github.com/ESloman/bsebot/commit/aa0d3a767eb8b8de936040103306e3f260691ae9))

* Bump xlsxwriter from 3.1.9 to 3.2.0 (#571) ([`a44630b`](https://github.com/ESloman/bsebot/commit/a44630bb1547ee74e3099bcbb8ad4a24006dd83f))

* Bump pymongo from 4.6.1 to 4.6.2 (#573) ([`725b4f1`](https://github.com/ESloman/bsebot/commit/725b4f1e758498da06d4389d7c7a0f71cfba8eeb))

* Bump selenium from 4.17.2 to 4.18.1 (#574) ([`ac857d6`](https://github.com/ESloman/bsebot/commit/ac857d67de83d1d805d4fa8c3f338a694f222aa7))

* Fix some more errors (#576)

Fix an error with awards
Fix an error with emojis ([`0a4e48f`](https://github.com/ESloman/bsebot/commit/0a4e48f879b2ad302043bb302ebf1e67a4837753))

* Fix some awards errors (#575)

* Make sure awards defaults aren&#39;t None
* Fix a number of awards errors
* Fix some linting issues
* Update chromedriver URL ([`9038c5f`](https://github.com/ESloman/bsebot/commit/9038c5f62d8a4e285329fd02d484a1c80891478b))

* Add some additional awards (#569)

* Add a &#39;most alphabetical&#39; award
* Add an award for most yellows ([`1f60f86`](https://github.com/ESloman/bsebot/commit/1f60f863c5c0fdf609b8fc336fd39163a6ff4e79))

* Bump pytest from 7.4.4 to 8.0.0 (#564) ([`abab480`](https://github.com/ESloman/bsebot/commit/abab480783dc26744cdeeaa9b858cc635a499966))

* Bump pre-commit from 3.6.0 to 3.6.1 (#568) ([`128c521`](https://github.com/ESloman/bsebot/commit/128c521fa1343e1f58d6b7dc068eb4985c1e2934))

* Bump python from 3.12.1 to 3.12.2 (#567) ([`24901e0`](https://github.com/ESloman/bsebot/commit/24901e06427c56444c55d6545e18b094fffd3f36))

* Fix some recent errors (#566)

* Fix a few recent errors
* Update wordle as well ([`1315560`](https://github.com/ESloman/bsebot/commit/1315560318977917885353b0a6d5945ba5e84371))

* Fix StopIteration exception (#565) ([`2f5babf`](https://github.com/ESloman/bsebot/commit/2f5babfa659c206ae0f5a400ffff44406ccff444))

* Bump docker/metadata-action from 5.5.0 to 5.5.1 (#563) ([`cc11154`](https://github.com/ESloman/bsebot/commit/cc111549b260421681d813d8cbf9e0b065673878))

* Fix bug with duplicate links and add more tests (#562) ([`b40d764`](https://github.com/ESloman/bsebot/commit/b40d7644b30c6e2950b6a8ba3de47f097d40be3c))

* #555 - Add channel cache (#560)

Add channel cache to cache channel names for easier retrieval ([`df89ee3`](https://github.com/ESloman/bsebot/commit/df89ee3786004d31ebec619a41828e445129f51c))

* Add tests for the API classes (#559)

- add tests for github class
- add tests for giphy class ([`21470f2`](https://github.com/ESloman/bsebot/commit/21470f2b039c550811aaba83822e7e80cc4662ea))

* Fix some type hints (#558)

- remove anything to do with releases/updates
- resolve some circular import type hint shenanigans by only importing the offenders in `if TYPE_CHECKING` blocks
- add tests to cover the changed code
- fix some other bugs ([`22cd401`](https://github.com/ESloman/bsebot/commit/22cd40182deb87cd5959b8ae4bb51dd06a5ad844))

* Fix some sonar issues (#557)

Fix some sonar issues
Add basic init tests to cover the changes ([`788b915`](https://github.com/ESloman/bsebot/commit/788b915288d38b0d7bdacd7204903e647febdcce))

* Update README.md and CONTRIBUTING.md (#556)

Update docs ([`90a8018`](https://github.com/ESloman/bsebot/commit/90a80180657a8b7721e0907ac7fcfc8146215a20))

* #398 - Update to use Dataclasses over TypedDicts and add more comprehensive testing (#547)

This is probably the largest PR being submitted at once - it&#39;s a shame that these changes will largely go unnoticed by the userbase and should be relatively seamless. The aim is to make it easier to contribute to the repository and make the codebase more resilient. The former is achieved with better type hints and better consistency when using database interactions. The latter is achieved with better testing (both in quantity and quality) and reducing the number of SonarCloud issues.

Massive refactor to use dataclasses over TypedDicts. Changes:
- changed typed dicts to dataclasses (and refactor the file structure for datatypes)
- refactor mongo classes to remove unnecessary intermediate class
- refactor mongo classes to enforce a `make_data_class` method
- refactor mongo queries to return whatever `make_data_class` returns
- add a &#34;minimum_projection&#34; level to allow us to set minimum projections to ensure our dataclasses can always be instantiated
- update everywhere to use new dataclasses
- add an entire suite of tests for all the dataclasses and database classes using mock data

Other changes unrelated to the main objective:
- remove some unnecessary/deprecated methods that weren&#39;t being used
- update README.md and CONTRIBUTING.md
- fix a host of sonar issues across the board
- refactor a few of the classes to reduce complexity where possible
- optimise some of the stats stuff to make less API calls
- make it easier to test/debug the stats stuff
- switch all datetime stuff to UTC
- updated a whole bunch of type hints
- added test suites for other areas of the code as well ([`0461499`](https://github.com/ESloman/bsebot/commit/0461499bd14cd03e45d9e94f0f0bbfe14e5d1b45))

* Another fix ([`d5690d5`](https://github.com/ESloman/bsebot/commit/d5690d57a32a037a6e24699688765979a8463e0c))

* Fix errors with awards ([`839cb73`](https://github.com/ESloman/bsebot/commit/839cb73a3caedcc5b614de150de2dd0c057b78fa))

* Bump seaborn from 0.13.1 to 0.13.2 (#551) ([`88add04`](https://github.com/ESloman/bsebot/commit/88add04caab5e2f801095048278f98a0c1b6f891))

* Bump selenium from 4.16.0 to 4.17.2 (#552) ([`4efbf18`](https://github.com/ESloman/bsebot/commit/4efbf18ef9bc2cce9375b67fed5baae301e1f64c))

* Bump python-dotenv from 1.0.0 to 1.0.1 (#553) ([`d3b8b6f`](https://github.com/ESloman/bsebot/commit/d3b8b6f2d1dd10170274a26ddbe04014fd6ecfb4))

* Fix error with placing bets (#549)

Catch an additional exception type. `child.values` can now be `None`. Fix for all views. ([`d5e842e`](https://github.com/ESloman/bsebot/commit/d5e842eff119b97198ac1f9c37b31ac0ce305c4e))

* Fix error with `/create` (#548) ([`42a0cc9`](https://github.com/ESloman/bsebot/commit/42a0cc92840aa683afa5713e15172f99eac0e4a2))

* #544 - Add additional wordle awards (#545)

Adds two new awards:
- most symmetrical wordles
- most green wordles

Fixes some other misc issues. ([`261ce3b`](https://github.com/ESloman/bsebot/commit/261ce3becda83ba38267a8b2f255cb5ee25d0901))

* Tidy up and fix some configuration (#542)

- Update Dockerfile to remove unnecessary bits
- Update .dockerignore to reduce docker image size
- Update .gitignore
- Trim down the README.md
- Update sonar-project.properties to specify Python version(s)
- add coverage config to pyproject.toml
- fix a bug
- update ruff config ([`abc318b`](https://github.com/ESloman/bsebot/commit/abc318b61725bf56ca616c6bd8bde6fcac3efaf2))

* Add reaction for wordle symmetry (#541)

- add reaction when Wordle result is symmetrical
- add tests for Wordle reaction action ([`9886a52`](https://github.com/ESloman/bsebot/commit/9886a52135f7000f6a8321200e109529e62325e6))

* Bump docker/metadata-action from 5.4.0 to 5.5.0 (#539) ([`5e5b815`](https://github.com/ESloman/bsebot/commit/5e5b8155cf3978f81346526a7f0dc1d368e022a0))

* Bump actions/setup-python from 4 to 5 (#540) ([`17bbc08`](https://github.com/ESloman/bsebot/commit/17bbc0898f476d1db449a7ef6c83608b4c08c4a4))

* Add SonarCloud integration (#538)

- Add sonar analysis
- Update README.md to include sonar badges ([`1946b75`](https://github.com/ESloman/bsebot/commit/1946b75379ef313d31fa12d5e9094e9a55902a6b))

* Bump python from 3.11.5 to 3.12.1 (#528) ([`39ae6e1`](https://github.com/ESloman/bsebot/commit/39ae6e1f1785d5219f782d55091ff285a1c091ef))

* Add test framework + tests (#537)

Add basic framework for testing using pytest + mocks.
Adds tests for a few things - new tests should be added over time. ([`a436c40`](https://github.com/ESloman/bsebot/commit/a436c4097c1dd2fbea2ab5114847a8656472d76c))

* Bump seaborn from 0.13.0 to 0.13.1 (#535) ([`04c58a5`](https://github.com/ESloman/bsebot/commit/04c58a5bdbf84443b136aba81952d3e2f41079ab))

* Bump pytest from 7.4.3 to 7.4.4 (#534) ([`fe2770c`](https://github.com/ESloman/bsebot/commit/fe2770c818d5384f8473324c2c3d4a72af15bfbc))

* Bump ruff from 0.1.8 to 0.1.9 (#533) ([`dd08a5d`](https://github.com/ESloman/bsebot/commit/dd08a5d6bd8dd54894fcfd430032d4506abfa45f))

* Some misc fixes (#536)

- Prevent awards from repeating entries
- Let wordle task print the words it guessed
- Removed some incorrect bits from comments ([`f55affd`](https://github.com/ESloman/bsebot/commit/f55affd061077227a8e1336240bbfab5364d1db8))

* Fix the stats comparisons (#532)

Fix the stat comparisons. Hopefully this will actually show us some data now. ([`7097f7f`](https://github.com/ESloman/bsebot/commit/7097f7fc78a8cdf727ff7089ba7627c65b8d5bba))

* Bump selenium from 4.15.2 to 4.16.0 (#527) ([`9b8cc39`](https://github.com/ESloman/bsebot/commit/9b8cc39d726ed9a4650dc47b66663bd82f4ed5ed))

* Bump pre-commit from 3.5.0 to 3.6.0 (#525) ([`ba78bbf`](https://github.com/ESloman/bsebot/commit/ba78bbf73632a26e293c42624e09e2aebe3a28ad))

* Bump actions/setup-python from 4 to 5 (#529) ([`fc97eb4`](https://github.com/ESloman/bsebot/commit/fc97eb47017a151350b38c9bed9c933477da133a))

* Bump docker/metadata-action from 5.3.0 to 5.4.0 (#530) ([`5a0df18`](https://github.com/ESloman/bsebot/commit/5a0df18c8aab1583c539d24fc1ebb3c455bd8088))

* Bump ruff from 0.1.6 to 0.1.8 (#531) ([`5035546`](https://github.com/ESloman/bsebot/commit/5035546500aeaa3495586dae575fd15b5597f39a))

* Make sure that sheldon gets eddies for his guess of one (#524) ([`b4701ae`](https://github.com/ESloman/bsebot/commit/b4701aebaae7d995a36c34950c44352366c878e2))

* Fix error when King isn&#39;t earning any eddies (#523) ([`3cbc154`](https://github.com/ESloman/bsebot/commit/3cbc1543f11c41d7d2bcac769b93d2d28805f320))

* Fix the salary error (#522) ([`9578f1f`](https://github.com/ESloman/bsebot/commit/9578f1f186c3ea6457132ef8ffb95d15c2994634))

* Update to use fully use ruff for linting + formatting (#521) ([`5a005a1`](https://github.com/ESloman/bsebot/commit/5a005a161bcb59064b24a749efc8df4a0feabfc9))

* Bump pymongo from 4.5.0 to 4.6.1 (#519) ([`efa8808`](https://github.com/ESloman/bsebot/commit/efa8808b78365dd3989ab3756416a784c2529cb1))

* Bump docker/metadata-action from 5.0.0 to 5.3.0 (#520) ([`29d7c21`](https://github.com/ESloman/bsebot/commit/29d7c219271136c9d1ae6d5fa2aa98039e46ba6b))

* Bump ruff from 0.1.5 to 0.1.6 (#515) ([`939fec4`](https://github.com/ESloman/bsebot/commit/939fec4d0af897893276d1f454434cfdd46df8d9))

* Fix awards (#518) ([`9326011`](https://github.com/ESloman/bsebot/commit/932601153daf2e5a4f7b606b56dcf04cdf30d745))

* Fix awards (#517)

* Fix for no thread messages

* Another fix for an award ([`2affd4f`](https://github.com/ESloman/bsebot/commit/2affd4fba21f5d3953b91d91570578fd8ddebbc9))

* Fix for no thread messages (#516) ([`8709ce0`](https://github.com/ESloman/bsebot/commit/8709ce0a6dd785166a3c7d9946c4a70e53de6749))

* Bump pre-commit from 3.4.0 to 3.5.0 (#506) ([`433ba4b`](https://github.com/ESloman/bsebot/commit/433ba4bba1035a6673156c861737d43ca7a672b5))

* Bump xlsxwriter from 3.1.6 to 3.1.9 (#507) ([`585b47f`](https://github.com/ESloman/bsebot/commit/585b47fd132459c630c62bc2754d56eb9f385d5e))

* Bump pytest from 7.4.2 to 7.4.3 (#510) ([`4a5540c`](https://github.com/ESloman/bsebot/commit/4a5540c0b6dcd6373d3894f76339bdecf1e65a21))

* Bump selenium from 4.13.0 to 4.15.2 (#511) ([`a1c89fd`](https://github.com/ESloman/bsebot/commit/a1c89fdc218909fd49cbb1c807f4f81e4133ee34))

* Bump ruff from 0.0.291 to 0.1.5 (#513) ([`ad7fb74`](https://github.com/ESloman/bsebot/commit/ad7fb744c445f99adc7ebe6383f50e6d134cfb18))

* Documentation updates (#299)

- Update various files
- Add new files ([`cb4e446`](https://github.com/ESloman/bsebot/commit/cb4e4463d94898a195743c3d048bc476bbd909ca))

* Codify some further changes (#499)

- Set the bot as the winner if no-one else wins
- Fix a bug with scheduling
- Fix some bugs with the worst wordle award
- Further filtering in the wordle stats graph
- Don&#39;t send awards in Jan ([`31d025f`](https://github.com/ESloman/bsebot/commit/31d025fe6461e86acb47488e2965e8227cb99819))

* Bump seaborn from 0.12.2 to 0.13.0 (#500) ([`412a04f`](https://github.com/ESloman/bsebot/commit/412a04ff6d795573a0b297fa317b90bf2a78a0e0))

* Bump xlsxwriter from 3.1.5 to 3.1.6 (#501) ([`a908de9`](https://github.com/ESloman/bsebot/commit/a908de97ccd013cc2f8206468b77fc03f7b19a5a))

* Awards Updates (#498)

Calculate best wordle average using the full unrounded value
Round to _4_ digits when displaying
Add in a debug mode that can be run with a simple change to the code in the docker container for when I want to test against a production dataset
Change the order of some stuff to make it easier to tell when something breaks
Don&#39;t give the bot eddies if the bot &#34;wins&#34; by default
Fix some errors with awards where some awards didn&#39;t have values
Add in worst average wordle award
Work out wordle averages using a greater degree of precision; only round the decimal points for display purposes ([`9538751`](https://github.com/ESloman/bsebot/commit/9538751715e7b10b57e91b74cbb83baec8e7a608))

* Bump selenium from 4.11.2 to 4.13.0 (#497) ([`05aa112`](https://github.com/ESloman/bsebot/commit/05aa112fe7cb498c7eb41f4dae681a43dabc6297))

* Bump docker/metadata-action from 4.6.0 to 5.0.0 (#490) ([`fde2acb`](https://github.com/ESloman/bsebot/commit/fde2acb0da0c706d226b24dfc68e008a60fd1889))

* Bump docker/login-action from 2 to 3 (#491) ([`57dbbde`](https://github.com/ESloman/bsebot/commit/57dbbdeb3b4ae2f2e3740c254b8d58578dd308d4))

* Bump docker/build-push-action from 4 to 5 (#492) ([`fbb850d`](https://github.com/ESloman/bsebot/commit/fbb850d710ca8ae399f5ec1367220afa3de5fa49))

* Bump xlsxwriter from 3.1.3 to 3.1.5 (#495) ([`718e2fe`](https://github.com/ESloman/bsebot/commit/718e2fe0e381dde2f2597c696a47db8dd21d7247))

* Bump ruff from 0.0.287 to 0.0.291 (#496) ([`ceb8543`](https://github.com/ESloman/bsebot/commit/ceb8543a38b6518b2e89eeb0235585d4d501724a))

* Bump xlsxwriter from 3.1.2 to 3.1.3 (#489) ([`a30f0c2`](https://github.com/ESloman/bsebot/commit/a30f0c207f055c76f6a1d32f0c004ad76124d452))

* Bump pytest from 7.4.0 to 7.4.2 (#488) ([`f181b39`](https://github.com/ESloman/bsebot/commit/f181b391ccde4ef9b88a5e816626d7ebef88c88e))

* Bump pre-commit from 3.3.3 to 3.4.0 (#485) ([`29f3919`](https://github.com/ESloman/bsebot/commit/29f3919655d3e7c64ea28098551248f2924456b1))

* Bump actions/checkout from 3 to 4 (#483) ([`e2ca356`](https://github.com/ESloman/bsebot/commit/e2ca356853473a0e1f2184490cbd349bf376550a))

* Bump ruff from 0.0.280 to 0.0.287 (#487) ([`dd8b2d0`](https://github.com/ESloman/bsebot/commit/dd8b2d0cf1bf638561b81c18b149b695e3a8c2ad))

* Various fixes and updates (#482)

* Fix error with wordle_solver
* Bug fixes
* Fix some bugs with bseddies awards
* Fix some linting issues
* Update twitter links
* Fix for chrome install
* More Dockerfile fixes ([`9713b2d`](https://github.com/ESloman/bsebot/commit/9713b2d1579b96f2c2ea34cda52b7b91f1435de6))

* Bump selenium from 4.10.0 to 4.11.2 (#475) ([`26b265e`](https://github.com/ESloman/bsebot/commit/26b265e332d3532fd05556ac4bb34b6a7d701700))

* Bump python from 3.11.4 to 3.11.5 (#479) ([`2cfa20d`](https://github.com/ESloman/bsebot/commit/2cfa20d3386db5da419186d2f60fa862ce1cd39a))

* Bump pymongo from 4.4.1 to 4.5.0 (#480) ([`a01b27c`](https://github.com/ESloman/bsebot/commit/a01b27ca9c5b530bce3b153490261bef77ccb85f))

* Bump flake8 from 6.0.0 to 6.1.0 (#473) ([`d2538d2`](https://github.com/ESloman/bsebot/commit/d2538d2db297b60bb974eafd2d47579d6c52cfb3))

* Fixes and updates (#474)

* Type check improvements ([`2e819c0`](https://github.com/ESloman/bsebot/commit/2e819c0d54e0b9270dca6bcb5566d921d94107bf))

* Fixes and Updates (#472)

* #462 - Reset role names

Reset role names after a &#39;successful&#39; revolution
Reset role names when a KING changes

* Vary starting word

Vary starting word so we try new ones
Add the word to the pool of starting words if we won quickly with it

* PEP8 fix

* Prevent duplicate links firing erroroneously ([`0599a61`](https://github.com/ESloman/bsebot/commit/0599a610502ac78a2f9004f26a67ed76af772430))

* Add chrome driver (#471)

* Add chrome driver ([`d4cc4ae`](https://github.com/ESloman/bsebot/commit/d4cc4aeaa2ed99ce551d090b03c13d8f98a504cb))

* #469 #468 Fix wordle bugs (#470)

Fix wordle stats
Fix wordle solver ([`38c69ff`](https://github.com/ESloman/bsebot/commit/38c69ffd208e96e8e98b214f8448230a60998be6))

* Bump webdriver-manager from 3.8.6 to 3.9.1 (#467) ([`557a7cf`](https://github.com/ESloman/bsebot/commit/557a7cf9065823adcca88e4ab36de66f73258973))

* Bump ruff from 0.0.278 to 0.0.280 (#466) ([`119a200`](https://github.com/ESloman/bsebot/commit/119a200a6461679468c943c38fda64dc69f53f4e))

* Bump ruff from 0.0.275 to 0.0.278 (#465) ([`853f5d4`](https://github.com/ESloman/bsebot/commit/853f5d4457f41d6f03022f1eeea4eb028c7b91da))

* Bump pymongo from 4.4.0 to 4.4.1 (#464) ([`5ab61e1`](https://github.com/ESloman/bsebot/commit/5ab61e1d86be15c39d1ac0d647aba3509d1f3303))

* Bump pymongo from 4.3.3 to 4.4.0 (#459) ([`de8e0b5`](https://github.com/ESloman/bsebot/commit/de8e0b5f0867c6a9a0ea98b1c9cf9a3721055c7f))

* Bump ruff from 0.0.274 to 0.0.275 (#460) ([`c118967`](https://github.com/ESloman/bsebot/commit/c1189672e2b470a4caae2a5d66b76875bd0dd0d0))

* Bump pytest from 7.3.2 to 7.4.0 (#461) ([`826247d`](https://github.com/ESloman/bsebot/commit/826247d48839f891fb025d5a7f4d13859cb4f9f8))

* Bump ruff from 0.0.272 to 0.0.274 (#458) ([`d31ea43`](https://github.com/ESloman/bsebot/commit/d31ea43f6be4cf8637378873322d3f8776e5bb39))

* Bump pre-commit from 3.3.2 to 3.3.3 (#456) ([`006229d`](https://github.com/ESloman/bsebot/commit/006229d478658ece5d5b3272556c45de28f0cade))

* Bump docker/metadata-action from 4.4.0 to 4.6.0 (#457) ([`0b37db1`](https://github.com/ESloman/bsebot/commit/0b37db1d331515be644c935ebe5a6845e93163cd))

* Bump selenium from 4.9.1 to 4.10.0 (#455) ([`86946f4`](https://github.com/ESloman/bsebot/commit/86946f4cecf2ca7b43d12b4ff06403a761ee4ba8))

* Bump ruff from 0.0.270 to 0.0.272 (#454) ([`5dddaf4`](https://github.com/ESloman/bsebot/commit/5dddaf4846f120928dff61cb321a65c290e6a691))

* Bump pytest from 7.3.1 to 7.3.2 (#453) ([`5be28f1`](https://github.com/ESloman/bsebot/commit/5be28f1665893da69a2b690faf004b64763ba02d))

* Bump python from 3.11.3 to 3.11.4 (#451) ([`3e276a5`](https://github.com/ESloman/bsebot/commit/3e276a596c3eb3473b63ce17efc34be0c3a09a71))

* Revert &#34;#398 - Change GuildDB and User to a dataclass&#34;

This reverts commit 5aadbb20a48f58265ffdcd9b21966bfbe06821b8. ([`8e0e646`](https://github.com/ESloman/bsebot/commit/8e0e646c8087221730136c928edbbf669815667d))

* #398 - Change GuildDB and User to a dataclass

Beginnings of the shift to dataclasses. Makes GuildDB and User dataclasses. ([`5aadbb2`](https://github.com/ESloman/bsebot/commit/5aadbb20a48f58265ffdcd9b21966bfbe06821b8))

* #446 - Add rigged message action (#450)

Adds a message action for users that say &#39;rigged&#39; shortly after a revolution ([`cd1080a`](https://github.com/ESloman/bsebot/commit/cd1080a3cae1a63c7b469287f434ca8907ee182d))

* #137 - Beginnings of a `/stats` command (#449)

Adds a /stats command for generating some stats. Can choose either quick stats or quick server stats for now.
Add some additional stats to /wordle as well. ([`455c020`](https://github.com/ESloman/bsebot/commit/455c02007a6fd16cc91a9cb2ad7c2d301c44ec26))

* #447 - Allow everyone to use `/taxrate` (#448)

Allows everyone to use `/taxrate` command
Used by &#39;normal&#39; users; will simply show the tax rate
Used by the &#39;King&#39;; will also allow them to change the rates ([`bfddf89`](https://github.com/ESloman/bsebot/commit/bfddf892d24e58aa8bc8b016270776a481d65615))

* #444 - Wordle Refactor (#445)

Refactors various different Wordle related things:
- fix bug with wordle stats not working sometimes
- get wordle starting words from the database
- allow wordle starting words to be configured via /config
- wordle starting words are weighted by their success rate
- allow wordle reminders to be configured via /config
- move all wordle config to just one &#34;Wordle&#34; option that has sub-options

Other stuff changed:
 - add AttributeError to selects try/except
 - fixed bug with Marvel Unlimited AD
 - remove bet ID from bet embed
 - add /place mention to bet reminders ([`d4fc886`](https://github.com/ESloman/bsebot/commit/d4fc886ce3a265ffced840ed03ae2e4f0fa49aa7))

* Add a &#34;halfway&#34; bet reminder (#443)

* Update betreminder.py

* Had halfway reminder for longer bets too

* Update betreminder.py

* Update betreminder.py ([`8de4c3f`](https://github.com/ESloman/bsebot/commit/8de4c3fbb2cd36061ff278e7fd65e768cf3b4939))

* Bump ruff from 0.0.267 to 0.0.270 (#440)

Bumps [ruff](https://github.com/charliermarsh/ruff) from 0.0.267 to 0.0.270.
- [Release notes](https://github.com/charliermarsh/ruff/releases)
- [Changelog](https://github.com/charliermarsh/ruff/blob/main/BREAKING_CHANGES.md)
- [Commits](https://github.com/charliermarsh/ruff/compare/v0.0.267...v0.0.270)

---
updated-dependencies:
- dependency-name: ruff
  dependency-type: direct:production
  update-type: version-update:semver-patch
...

Signed-off-by: dependabot[bot] &lt;support@github.com&gt;
Co-authored-by: dependabot[bot] &lt;49699333+dependabot[bot]@users.noreply.github.com&gt; ([`5db399b`](https://github.com/ESloman/bsebot/commit/5db399b57c47eb68a9d2bb6783fa21c2e2194de8))

* #443 - Activities updates (#442)

* #433 - Allow entering multiple activities at once
* Change the frequency of changes ([`4035ef7`](https://github.com/ESloman/bsebot/commit/4035ef7a1c4d9ef125aeddce3fed3f7e3006e719))

* Bump xlsxwriter from 3.1.0 to 3.1.2 (#441) ([`cb2f1d8`](https://github.com/ESloman/bsebot/commit/cb2f1d8804a42ceece4cadb03d669d3beac67711))

* Bump pre-commit from 3.3.1 to 3.3.2 (#439) ([`0594cdf`](https://github.com/ESloman/bsebot/commit/0594cdf3a38b346bc40e0dfd1e5a1d70e538484a))

* Bump requests from 2.30.0 to 2.31.0 (#437) ([`6bb20b7`](https://github.com/ESloman/bsebot/commit/6bb20b7b8f70d8fdcaa98f29c44cb22ba795ac28))

* Various bug fixes (#435)

Fix error on startup with user getting
Fix indentation level for daily summary message
Fix typo in config
Use markdown formatting for main config message
Fix wordle not working due to new screen ([`c3b32b0`](https://github.com/ESloman/bsebot/commit/c3b32b01330d55c753e2dd378235aa63b75ea9f7))

* #382 - Markdown changes (#387)

* #382 - Update markdown stuff

Beginnings of updating bot messages to better leverage the new markdown capabilities

* #382 - Markdown stuff

Make one of the vally messages super large
Add some more wordle reminder messages

* #382 - Markdown stuff

Update to revert back to embed and with formatted title

* #382  - Markdown stuff

Add a random embed colour

* Fix typo

* Update help.py

Add remind me help options
Wanted to have this formatted with markdown without merge errors so added it here. Remind me functionality added as part of #293.

* Make sure new suggest modal has markdown changes

* #387 - Markdown changes

Make more changes to markdown stuff with the new things we&#39;ve added recently ([`0bc2853`](https://github.com/ESloman/bsebot/commit/0bc285372c2a3a44857953644aae6f0acbdb3b6c))

* Sticker updates (#432) ([`9cafd38`](https://github.com/ESloman/bsebot/commit/9cafd3821f087f59613c64cac5a5b057e403221b))

* Bump ruff from 0.0.265 to 0.0.267 (#431) ([`a91237f`](https://github.com/ESloman/bsebot/commit/a91237f516d8c34c30dd7da2723d0e76c3bf3ed8))

* Tweaks to activity changer (#430) ([`c48cd71`](https://github.com/ESloman/bsebot/commit/c48cd715d87565a4c6fa7d2e38c1863da64e4f74))

* #427 - Allow adding bot activities through /config (#428)

Allow adding bot activities through /config
Add infrastructure for letting users add new bot activities
Modify the activity task to pick these from the database ([`e2b7877`](https://github.com/ESloman/bsebot/commit/e2b7877d327f2473176d2f493607ca4e1dae99c4))

* Bump selenium from 4.9.0 to 4.9.1 (#425) ([`ee5fbc6`](https://github.com/ESloman/bsebot/commit/ee5fbc68b80893681bcfa6e475b97de4cd5d5f57))

* Make logging less verbose for revolution event (#429)

Make logging less verbose ([`dd3fa03`](https://github.com/ESloman/bsebot/commit/dd3fa03222e7331f74efd229710784a592e4e23b))

* Bump ruff from 0.0.263 to 0.0.265 (#423) ([`12bff86`](https://github.com/ESloman/bsebot/commit/12bff86df777f5250f80a17aede2feaa673cc9c3))

* Bump requests from 2.29.0 to 2.30.0 (#424) ([`1ff4cf4`](https://github.com/ESloman/bsebot/commit/1ff4cf42f7d1992c868eb197d81a9db0fdb24c74))

* Bump pre-commit from 3.2.2 to 3.3.1 (#426) ([`9cc933c`](https://github.com/ESloman/bsebot/commit/9cc933c86426d1eee267ffd25a6deef5d23bfea4))

* #420 - Add more wordle stats (#422)

Add more wordle stats
Add a graph for average over time
Add a share button ([`2509fab`](https://github.com/ESloman/bsebot/commit/2509fab8b1869fbb13bf68717729ab12996374e7))

* #419 - Don&#39;t be as hasty with command suggestions (#421)

- Amend regex for matching command names
- Remove bet fields update as we&#39;ve done that now
- Fix bug with message references in other servers that we don&#39;t have permissions for ([`85dd756`](https://github.com/ESloman/bsebot/commit/85dd756239d901d2a8574d7348e967f32cfd711f))

* Various enhancements and fixes (#418)

This is a large PR that resolves a number of open issues and adds a bunch of stuff that isn&#39;t in issues.
Includes:
- Allow users to gift to other users as a context menu command (#73)
- Getting wordle config from guild configuration and adding functionality to change that (#307, #250)
- Adding beginnings of some unit tests. This is for non-discord related functionality. (#130)
- Add a dynamic help command (#417)
- Add BSEddies configuration options (#250)
- Allow users to add autogenerate bet options (#250, #330)
- Fixed some typos in places
- Add a command suggestion message action
- Added a `/wordle` stats command
- Add some debug logging to places
- Allow admins to get the eddies message summary message (and added needed configuration)
- Fix some bugs with user_ids still
- Add more `delete_afters` ([`b7ce1bf`](https://github.com/ESloman/bsebot/commit/b7ce1bfc55dcbabf5d3182933d432e2648b77655))

* #82 - Create an activity task (#416)

This is a basic implementation of an activity task. Randomly picks an activity from the activity options (default weighted higher).
If the activity needs a name, it picks one randomly from the list of available options.
Can be expanded later. ([`eb640d5`](https://github.com/ESloman/bsebot/commit/eb640d55763b4a4e9517d1c1e7558f1569c60c8c))

* Bump ruff from 0.0.262 to 0.0.263 (#414) ([`a325c17`](https://github.com/ESloman/bsebot/commit/a325c17f00c47de743334c95b24336b4a6654c14))

* Bump requests from 2.28.2 to 2.29.0 (#415) ([`ea82da1`](https://github.com/ESloman/bsebot/commit/ea82da149e4c89d23348414d04fd3b585f1cd17c))

* Some bug fixes (#413)

- Fix error with some slash commands not working
- Remove UTC stuff from BSEddies ([`613debb`](https://github.com/ESloman/bsebot/commit/613debb39d300649a67ae2c1e9b93a0cc4ce4c9e))

* #109 - Add comparisons to previous stats (#412)

- Add basics of adding comparisons to previous stats
- Works for a few simple stats
- Not tested yet lol ([`174eaf8`](https://github.com/ESloman/bsebot/commit/174eaf807e0ac8e14d9bc336e80302b543a9be4a))

* #410 - Allow some hardcoded odds (#411)

Allows some hardcoded message odds. This works by adding a tuple to the list of message strings and defining the message string and the odds (roughly out of 100) as a float.

Updated message string docs and add an example. ([`59deebf`](https://github.com/ESloman/bsebot/commit/59deebfddf2db4c9c6bc0a8fc8928f8ed975456e))

* #408, #102 - Dynamic random message odds (#409)

Add functionality that allows us the odds of random messages to be a bit more dynamic. Rather than each message having equal chance, give those messages that have been used less a bit more chance to be picked. Hopefully increasing the diversity of the messages chosen. Functionality added for Valorant daily rollcalls and Wordle reminder messages. Added into a function in utilities.py so that it can be reused in other places that will use it.

Also make sure we&#39;re sending different messages for each wordle reminder on the same day. ([`1dbf375`](https://github.com/ESloman/bsebot/commit/1dbf375640b481ec445e1abeb7ec9f4a31297fe7))

* #402 - Tough one (#407)

- Send a meme when most people get 6/6 for wordle
- add the logger to all the message actions ([`a56bec4`](https://github.com/ESloman/bsebot/commit/a56bec494f3e2a36788e8b1adee95b4a2bbcb7a5))

* #404 - Additional message actions (#406)

Added two new message actions:
- a `remind me` message action, triggering if it seems the user wants to set a reminder. This informs the user about the possibility of using the bot to set a reminder. This is on a cooldown
- a `duplicated link` message action. This triggers if the same link was posted in the same server within the last couple of days. ([`12c3da2`](https://github.com/ESloman/bsebot/commit/12c3da2fb866657ad9e89fadf2ce2392ee161715))

* Bet updates (#241, #332) (#405)

This update is threefold:
- Allow the creator of the bet to add another option post-creation
- Allow users to change their bets to some extent
- Add some extra top-level fields for bets that will make future easier (#403)

Users will only be able to change their bets 5 minutes after they placed theirs, or five minutes after a new option was added. This is mainly targeting the use case where people place on one outcome accidentally or wish to change it after placing it too quickly without thinking. Adding a new bet option allows users to change their existing bets if they want to change it to the new one. Made it five minutes to prevent users changing a bet after the real outcome becomes clear; though this might be changed in the future to be a certain fraction of the total bet time (longer bets should have more leeway for changing their mind). ([`0e284cf`](https://github.com/ESloman/bsebot/commit/0e284cf7254c1fe58f76a503766f8d45ce4c1540))

* Bump ruff from 0.0.261 to 0.0.262 (#401) ([`0bcb2ef`](https://github.com/ESloman/bsebot/commit/0bcb2efd0f9244ae874c11eff2fa732b691372fb))

* Bump selenium from 4.8.3 to 4.9.0 (#400) ([`224df54`](https://github.com/ESloman/bsebot/commit/224df54917f5cc0fa92bb64c89850bb55b8497b0))

* Bump docker/metadata-action from 4.3.0 to 4.4.0 (#399) ([`afcdbb6`](https://github.com/ESloman/bsebot/commit/afcdbb6d933264989d210c17a758c20fdff79848))

* #393 - Message strings (#394)

Add a central director for some message strings. This is where each file can denote a particular set of messages to be chosen randomly by the bot. Allows simpler editing of some files without having to go looking for their locations.

Will endeavour to add more to this going forward. ([`c0de7b9`](https://github.com/ESloman/bsebot/commit/c0de7b99c14ab3793ef44e37c3f820ef0536ccbe))

* Bug fixes (#397)

Fixes #396; duplicated `user_id` entry
Resolve some errors in the logs with `NotFound` errors with view timeouts ([`9906912`](https://github.com/ESloman/bsebot/commit/99069122200b7043d2a7c120d4e305ca98a20028))

* Fix bug (#395)

Thread config still wasn&#39;t letting me configure threads - need to pass in the guild ID to the permissions checker and the user ID now ([`22a5d5c`](https://github.com/ESloman/bsebot/commit/22a5d5c6a303b30e3164f70d0e040cafeee920fb))

* Quality of Life Changes (#392)

A host of QoL changes for the users and the repo:

[User]
    Add delete_after on a lot of ephemeral confirmation messages to automatically remove them. Users should be clearly them theirselves but this will do it if they don&#39;t.
    Remove some information from the revolution embed
    Add a config option to enable/disable receiving the daily salary message (works in servers and in DMs)
    Fix a bug where thread configuration wasn&#39;t showing correct threads
    Make /config filter configurable items from the start to prevent user confusion
    Make datetimes simpler on leaderboards
    Hide UI views in places they&#39;re no longer viable

[Repo]
    Add more to the .dockerignore so that the docker image is tidier
    Add ruff cache to.gitignore
    Refactor clienteventsclasses so that the init is clean (helps with circular imports in the long run)
    Rename all the slash command classes
    Refactor modals so that each modal has their own file in their own directory
    Fix some incorrectly named functions
    Add optional sort option to database queries
    Add optional many param to database updates. Make sure this is false be default. ([`d908dd0`](https://github.com/ESloman/bsebot/commit/d908dd0dba129d25af42df3cef8519c54d5fb4a9))

* #128, #121 - Revolution view refactor (#391)

* #128 - Reduce revolution view complexity

Refactor revolution view to remove a lot of the duplicated code.
All the logic is now abstracted to `_revolution_button_logic` and handles the logic for all buttons. This reduces the amount of duplicated code in the class.
I have also added lots more comments in the hope of making it clearer to understand.

* #121 - Add impartial button
Allow users to be &#39;impartial&#39;. This means users can make a conscious decision to not care! Either not doing anything at all or resetting their existing choice without actively choosing the other faction. ([`fc06f2d`](https://github.com/ESloman/bsebot/commit/fc06f2d784cc30611b1d777aa158b2ecea3fcd7b))

* #296 - Add Task Manager (#389)

Beginnings of Task Manager implementation and general tasks refactor.
- Add `task` property to BaseTask
- Make sure all tasks set property correctly
- Add task manager that loops through all the tasks periodically and makes sure they&#39;re running
- Actually make sure all loops have a correct doc string
- Add some typing to BaseTask
- Correct typo in all socket methods
- Add cog_unload function to BaseTask
- Added type hints to various places that needed them ([`7e3aea8`](https://github.com/ESloman/bsebot/commit/7e3aea81194b37aca4d79f191ef6559295a65bc0))

* Bump webdriver-manager from 3.8.5 to 3.8.6 (#386) ([`20b479c`](https://github.com/ESloman/bsebot/commit/20b479c0b308dff8f67841a0051ca15475ea2ea2))

* Bump xlsxwriter from 3.0.9 to 3.1.0 (#385) ([`584bc6a`](https://github.com/ESloman/bsebot/commit/584bc6a6116d4ddc0b2c180f720789ccb6e9c8f5))

* #293 - Add /remindme functionality (#388)

Add functionality for reminders. There are two ways to create a reminder:
- using a slash command `/remindme`
- right-clicking a message and using a context menu command
Both methods will trigger a modal to be filled out. This will then enter a reminder into the database.

A new task has been added to check for expired reminders. ([`1b2d40c`](https://github.com/ESloman/bsebot/commit/1b2d40c8c1a50d02afca989eebef54671174dd73))

* #381 - Voice message support (#383)

Voice message support ([`97c04bc`](https://github.com/ESloman/bsebot/commit/97c04bc47128ce1458b8c4c2afe022af5108c168))

* #83 - Automatically restart the bot (#384)

Add bash file for automatically restarting the bot. This is already running every few days via cron. This allows changes to go in, get approved, and merged into main and then picked up automatically without me having to log in to the server to apply them. ([`c441cf8`](https://github.com/ESloman/bsebot/commit/c441cf89f23deb34c697b743f8f33c3b9a3c8418))

* #250 #178 - Add revolution config stuff (#380)

Add config option for revolution event; allows disabling/enabling of revolution event ([`4d28b2d`](https://github.com/ESloman/bsebot/commit/4d28b2d54b7dc9a2292e185f90a23a313ba9a9c8))

* Bump pre-commit from 3.2.1 to 3.2.2 (#379) ([`5ba3257`](https://github.com/ESloman/bsebot/commit/5ba32579408d33a2f2c7e187a82b688c6e25464c))

* Bump ruff from 0.0.260 to 0.0.261 (#378) ([`104d73b`](https://github.com/ESloman/bsebot/commit/104d73b5491b52f825945dc264fa5eca32da0c0c))

* Bump python from 3.11.2 to 3.11.3 (#377) ([`f4b5b49`](https://github.com/ESloman/bsebot/commit/f4b5b49f414d4763845b9d70544895eea12cc18d))

* Update wordlereminder.py (#376)

* Update wordlereminder.py

Updates to the wordlereminder task to add some new messages for when people forget their Wordle

---------

Co-authored-by: esloman &lt;elliot.sloman@hotmail.com&gt; ([`fbe6dff`](https://github.com/ESloman/bsebot/commit/fbe6dffa62bae31993803f9acbf92760f3932df6))

* Fix bugs with UTC stuff (#375)

Convert our start/end stuff when dealing with interactions to UTC aware datetimes so we don&#39;t miss messages ([`baf8c0c`](https://github.com/ESloman/bsebot/commit/baf8c0c73474d6748ef40eafe87aef8e2d3885fc))

* Fixing BSEddies bugs (#374)

Fix a couple of bugs with recent stats and awards ([`6b9e9cc`](https://github.com/ESloman/bsebot/commit/6b9e9ccb79e8d5069e278925123f808a88d8c01f))

* Bump ruff from 0.0.259 to 0.0.260 (#372) ([`b72ce35`](https://github.com/ESloman/bsebot/commit/b72ce35c2e5a61d0e7b07daad91ffe7212f02253))

* #333 - Allow bets to have multiple winners (#373)

- modify `close` and related things to allow bets to have multiple winning outcomes. Users can still only select one outcome.
- fix some naming issues
- fix a circular import
- tidy up guildchecker a bit ([`6c6b880`](https://github.com/ESloman/bsebot/commit/6c6b880fa6f402c9f0f3a46607e5d10f2c6c9975))

* Update dependabot.yml

Change checks to weekly ([`7376f81`](https://github.com/ESloman/bsebot/commit/7376f81c36e3c243f6d1b967d62129e9a3b3cba2))

* Various bug fixes and improvements (#371)

- Make sure tax rate message includes support value #326 
- Fix message sync failing on channels it doesn&#39;t have access to
- Don&#39;t trigger actions on message sync
- Add context command structure ([`4b2ddf2`](https://github.com/ESloman/bsebot/commit/4b2ddf28f9d107fd73422bb40cd2fa6995d907b7))

* Add message sync task (#370)

* Add message sync task
* Don&#39;t trigger on_message_edit for ephemeral messages ([`b9ed299`](https://github.com/ESloman/bsebot/commit/b9ed2997ac68c2d67c83e155cd209eb39397008e))

* #250 - Add admin config stuff (#369)

- Added admin config stuff
- Use admin list for making sure only certain users can configure things ([`1b28f7b`](https://github.com/ESloman/bsebot/commit/1b28f7be5dcd7ca5df21d239ffd145b77aea5911))

* #250 - Add additional configuration options to `/config` (#368)

Added:
- wordle config options (can now turn wordle off, set the channel, enable/disable wordle reminders)
- valorant config options (can now turn valorant rollcall off, set the channel, set the role)
- salary config options (can now set the daily minimum amount of eddies)

Added database entries in guilds for each new option and use those options in the various places they&#39;re required. ([`59a53a6`](https://github.com/ESloman/bsebot/commit/59a53a622e6658d64526dc9a71c9f1471f5ad5d7))

* #331  - Add VC select to `/autogenerate` (#367)

This refactors the autogenerate section and adds another select, for the voice channel to fill from, to the View.
- Instead of doing everything in callbacks, rely on a `update` method on the root view for handling state.
- Added a &#34;paginated&#34; method to split the number of selects across two &#34;pages&#34;. User must fill in the first section first and then move on to the second page.
- VC select selects the voice channel that user option will be filled from rather than using the channel ID in the bet data type. This fulfills a bit of #71 to allow the project to be a bit more server independent. ([`7d9ed1e`](https://github.com/ESloman/bsebot/commit/7d9ed1e24833035d8af6657494d82c90045f09fe))

* #327 - Refactor timeout string converstion (#366)

- Add utility function `convert_time_str` for converting a time str to an integer for total seconds. Use this function in `/create`.
- Add support for adding timeouts using &#34;weeks&#34; as well
- Fix a couple of bugs with some bet view functions ([`732127c`](https://github.com/ESloman/bsebot/commit/732127c135bd22c1972f4ae7f216182a2d852715))

* #322 - Application commands and direct messages (#365)

- Stop _all_ slash commands from working in DMs unless the `self.dmable` attribute is set.
- Refactor `/view` to let it work in DMs; to prove that we can have functional slash commands in direct messages.
- Add extra functionality to guild sync that keeps the name updated
- Updated GuildDB type to add name attribute ([`c47dbee`](https://github.com/ESloman/bsebot/commit/c47dbee270f45108064536f182cc00e90da85474))

* Bump selenium from 4.8.2 to 4.8.3 (#364) ([`be0fca7`](https://github.com/ESloman/bsebot/commit/be0fca719ba5caad1a47ea8c2e6cdb1268a09336))

* Bump pre-commit from 3.2.0 to 3.2.1 (#363) ([`a1cc9f1`](https://github.com/ESloman/bsebot/commit/a1cc9f1e0ab98e4a867f445f39ad2b54110be157))

* Bump ruff from 0.0.258 to 0.0.259 (#362) ([`2805790`](https://github.com/ESloman/bsebot/commit/2805790accda048f885a569a803d06800d0c3f18))

* Bump ruff from 0.0.257 to 0.0.258 (#361) ([`6d75475`](https://github.com/ESloman/bsebot/commit/6d75475e137edf1dc2731cc96d0ddb4c88353359))

* #359 - Fix error with bot DM messages (#360)

Stop bot processing it&#39;s own direct messages to other users and failing
Start storing user names in the DB and add updating them to guild checker task ([`dc4fa3c`](https://github.com/ESloman/bsebot/commit/dc4fa3c0f7014ade146f807153c2f212098ccfff))

* #250 - Beginnings of `/config` and more thread control (#358)

- Add beginnings of /config command
- Allow users to change thread settings
- Modify thread client events to be better at joining old threads
- Add info about /config to thread messages telling users how to turn it off
- Make on_message ignore ephemeral messages
- Change thread mute reminders logic to be based on thread_info and not existing threads in general chat
- Refactor all of the slashcommand imports to remove init imports
- Refactor all of the views/selects imports to remove init imports ([`0f46550`](https://github.com/ESloman/bsebot/commit/0f46550426ac2488961a31d977c178945a97a84c))

* Bump ruff from 0.0.256 to 0.0.257 (#356) ([`223c014`](https://github.com/ESloman/bsebot/commit/223c014a04a2d3bfc0905481c9962183ef11ac1f))

* Bump pre-commit from 3.1.1 to 3.2.0 (#355) ([`7caa45c`](https://github.com/ESloman/bsebot/commit/7caa45c85ecd1074fa6989bbc760f95cd20d47ad))

* Bump py-cord[speed] from 2.4.0 to 2.4.1 (#357) ([`421f343`](https://github.com/ESloman/bsebot/commit/421f34313611cdab6e8c0b5867b088881e043950))

* Bump ruff from 0.0.255 to 0.0.256 (#354) ([`9183a30`](https://github.com/ESloman/bsebot/commit/9183a305bb9ddad3c517db20086b368445db297e))

* Fix some bugs with BaseTask implementation (#353) ([`77b382b`](https://github.com/ESloman/bsebot/commit/77b382b55a719a1da46a2f8c023643ef8bd3470e))

* Bump ruff from 0.0.254 to 0.0.255 (#352) ([`5bbedc6`](https://github.com/ESloman/bsebot/commit/5bbedc693a557c860bf8518eb47bc6cb37240f50))

* #329 - Add a BSE BaseTask (#351)

Added a BaseTask that all other tasks now inherit from. This makes things a little simpler as the BaseTask defines all the Collection clients and the shared methods (like checking start up tasks). This also unifies the naming conventions of all Collection classes.
Also the &#34;if BSE_SERVER_ID&#34; check for some tasks; those tasks were doing the same check within their loop so it was unnecessary.
Made wordle task guild independent.
Fixed a bug with revolution task. ([`ce5f1b1`](https://github.com/ESloman/bsebot/commit/ce5f1b1a9cd7e9ba7cb2eea7a4ce8c9b23e1a166))

* Bump xlsxwriter from 3.0.8 to 3.0.9 (#350) ([`cbc3b10`](https://github.com/ESloman/bsebot/commit/cbc3b10e6d97988a48ab325eebcee84087eec394))

* #324 - Create our own BSEBot class (#349)

* #324 - Beginning of adding our won BSEBot class
This inherits from `discord.Bot` but overrides `fetch_guild` and `fetch_channel`. The override adds a `get_guild` and `get_channel` respectively, this is in an attempt to limit API calls and improve performance/responsiveness.
Turn on debug logging for now whilst we evaluate ([`be3a4ea`](https://github.com/ESloman/bsebot/commit/be3a4eaacc1ddd9886355f9c3f72467269dbc7c5))

* #341 - Use a single MongoClient throughout rest of the code (#343)

Use singleton pattern for MongoClient ([`a271cd5`](https://github.com/ESloman/bsebot/commit/a271cd507c459b591762fbbb4b856dd55b856280))

* #337 - Make sure stats cache only gets needed transactions and activities (#347)

Make sure stats cache only gets needed transactions and activities
Use `interface.query` for paginated_query ([`297a5a8`](https://github.com/ESloman/bsebot/commit/297a5a83053ad27aba9bfdcfc10cdff3185ede5c))

* #344 - Revolution fixes (#345)

* Fix a bug with starting a revolution event
* Only create new events if it&#39;s exactly 4pm ([`ffb973f`](https://github.com/ESloman/bsebot/commit/ffb973fe20793a4e374ec9038353ad021050f633))

* Bump ruff from 0.0.253 to 0.0.254 (#348) ([`e910764`](https://github.com/ESloman/bsebot/commit/e91076402e2de7c3e52ca228cc08b5b3bf3d715e))

* Update README to correct workflow ([`6dbe36b`](https://github.com/ESloman/bsebot/commit/6dbe36b9ec08028172fa092d634f4860f9d150c6))

* Update ruff pre-commit version ([`63eb128`](https://github.com/ESloman/bsebot/commit/63eb1280380074ef3a0e9e5b6013709304fd74da))

* #335 - Stop letting bots win awards (#346)

Add a `is_bot` field to the database that&#39;s True if the message was from a bot
When collecting stats, don&#39;t use messages from bots ([`c5d72fe`](https://github.com/ESloman/bsebot/commit/c5d72fea60f68df0e911ff424b92c2438a4966b9))

* Fix login-action version ([`a315bfb`](https://github.com/ESloman/bsebot/commit/a315bfb8417af0d1af8495dbda9885d28457f8e4))

* #339 #130 - CICD changes (#342)

#339 #130 - CICD changes
Only push to dockerhub on main
Actually launch BSEBot docker container and test on PRs to main
Fix some errors
Tidy up dockerfile
Modify main.py to favour environment variables ([`e302418`](https://github.com/ESloman/bsebot/commit/e3024180c927694821b217090be0770fc3540c74))

* Mongo cached client fix (#340)

* This is a quick fix for threading issues with MongoClient and possibly creating too many instances of them
* Fix flake8 issues ([`05845ab`](https://github.com/ESloman/bsebot/commit/05845ab1e4aaa883846b1469cc56972e39bd3fe3))

* #336 - Make transactions and activities use a separate collection (#338)

- Add collection classes for transactions and activities
- Replace previous usage to new usage
- Simplify some logic so that the `increment_points` function handles the transaction adding
- remove `decrement_points` and just make sure we use `increment_points` with the amount made negative ([`d27e03c`](https://github.com/ESloman/bsebot/commit/d27e03cbbe963d71bd18b27776f524aef56ae39f))

* Bump pre-commit from 3.1.0 to 3.1.1 (#328) ([`35773d6`](https://github.com/ESloman/bsebot/commit/35773d6ed0ee835c93ccb03adf969841e4f56f92))

* #79 - Actually make commands work for multiple guilds (#325)

Switch to using &#34;global commands&#34; rather than guild commands ([`403a304`](https://github.com/ESloman/bsebot/commit/403a304f2bfe23cbdf2e85d5b9c97f2c06d037a3))

* Bump ruff from 0.0.252 to 0.0.253 (#323) ([`196941b`](https://github.com/ESloman/bsebot/commit/196941bf022ed251d20be5c899273c4041959e15))

* Fix some revolution woes (#320)

* #319 #317 - Fix some revolution woes
- use `fetch_` in places where `get_` returned None
- `_message.send` should be `_message.reply`
- better separate events for different guilds
- stop king task logging so much during revolution events (related to above)
- don&#39;t use bse channels as default

* #319 - Fix some revolution woes
Fix bug with king rename that wasn&#39;t sending the message

* #269 - Use silent for a lot more notifications
Use silent for all of the direct messages

* Make leaderboard show users with ten points when there aren&#39;t many users in the guild ([`d8e3a3a`](https://github.com/ESloman/bsebot/commit/d8e3a3a3c805ffdfaff51b1d18e01b2e548ce2ba))

* #79 - Remove guild restriction from all slash commands (#321) ([`79f0a8b`](https://github.com/ESloman/bsebot/commit/79f0a8b4b555bc25aebad064ddfe4844b1f639fe))

* Bump python-dotenv from 0.21.1 to 1.0.0 (#311)

Bumps [python-dotenv](https://github.com/theskumar/python-dotenv) from 0.21.1 to 1.0.0.
- [Release notes](https://github.com/theskumar/python-dotenv/releases)
- [Changelog](https://github.com/theskumar/python-dotenv/blob/main/CHANGELOG.md)
- [Commits](https://github.com/theskumar/python-dotenv/compare/v0.21.1...v1.0.0)

---
updated-dependencies:
- dependency-name: python-dotenv
  dependency-type: direct:production
  update-type: version-update:semver-major
...

Signed-off-by: dependabot[bot] &lt;support@github.com&gt;
Co-authored-by: dependabot[bot] &lt;49699333+dependabot[bot]@users.noreply.github.com&gt; ([`133c120`](https://github.com/ESloman/bsebot/commit/133c120f9d322dd38dc8ac246a6db84a41aed1d4))

* Bump pre-commit from 3.0.4 to 3.1.0 (#310) ([`8ee9700`](https://github.com/ESloman/bsebot/commit/8ee97008535f95be98f5ae1dbf7713a30b8b1e7b))

* Bump actions/checkout from 2 to 3 (#312) ([`b0bfad2`](https://github.com/ESloman/bsebot/commit/b0bfad201813bd7f003a9111d0817b54e6b18462))

* #237 - Message &#39;actions&#39; and Marvel Unlimited Ad (#316)

* #237 - Add Marvel Unlimited &#39;AD&#39;
Refactor `on_message` to add message actions
Use new system for message actions to add marvel ad ([`330bee6`](https://github.com/ESloman/bsebot/commit/330bee62f12303994e2503d8790a85f7bc6f6bdc))

* Add additional linting check (#314) (#313)

* #313 - Change linting
Add separate requirements file
Fix all the current lint issues
Rename linting file
Add ruff as linter ([`a66ed4c`](https://github.com/ESloman/bsebot/commit/a66ed4cf89c981076381e993bb65f04437a9d9bb))

* Update dailyvallytask.py (#309)

* Update dailyvallytask.py

* Update dailyvallytask.py ([`4080634`](https://github.com/ESloman/bsebot/commit/408063449358209cd8a0e0a0dce10e19e42df84d))

* Message pinning (#304)

* #298 - Add ability to pin messages ([`cc0675e`](https://github.com/ESloman/bsebot/commit/cc0675e50e39adcf33a5858eac346ed646f4c42e))

* Colour formatter (#303) (#302)

* #302 - Add colour formatter
This is a mostly an aesthetic change; make logs when debugging locally have colour
Move creating the logger to utilities.py
Don&#39;t log debug events when running in main

* #302 - Fix flake8 issue ([`0e9162a`](https://github.com/ESloman/bsebot/commit/0e9162afe371cd199703ec59cfc1a80423170251))

* #305 - Place command not working (#306)

Fix select option being too long with the title ([`2376de5`](https://github.com/ESloman/bsebot/commit/2376de5e856d221e25a807a7b01750a43b9a2e70))

* Bump selenium from 4.8.0 to 4.8.2 (#301) ([`467160d`](https://github.com/ESloman/bsebot/commit/467160d75454ad424b666d3bc772244caf33d480))

* Updates to ruff config ([`e38877c`](https://github.com/ESloman/bsebot/commit/e38877c6c5f7414ca79af89650d7022ca37326ce))

* Revolution fixes (#300)

* #297 - fix issue with /taxrate command
Set keyword properly
* #294 - Fix revolution error #4
No longer need the guild.id parameter for sending a gif function
* #295 - Make sure users always have a chance to overthrow
Cap the max chance at 95 and the min chance at 5
* Fix type hinting for find_user
* Only valorant bets should get filled
* #294 - Fix revolution error 5
get_role method doesn&#39;t need awaiting
* #294 - Fix for errors when one guild has an event and another doesn&#39;t
* #294 - Make sure we set supportertype in DB for supporters
* #294 - Fix &#34;king_since&#34; KeyError
* #294 - Fix checking for revolution events on startup ([`61f2596`](https://github.com/ESloman/bsebot/commit/61f2596b83b94abf7348fa151be32ae3caa348ad))

* Merge pull request #292 from ESloman/brods-patch-1

Update README.md ([`010a608`](https://github.com/ESloman/bsebot/commit/010a60807e1cd1a913dc91b7e544673be0cbdb21))

* Update README.md ([`f9b4a03`](https://github.com/ESloman/bsebot/commit/f9b4a03281fa79f0acebf0d83389ca2cfe7776d5))

* add release checker (#290) (#291)

Couple of tweaks:
- make wordle message silent
- remove erroneous comma

#290 - Add a release checker
Checks periodically for new github releases and posts release notes to discord ([`9725776`](https://github.com/ESloman/bsebot/commit/9725776086efa9194025663883b765d32d0a3fe2))

* esloman/various (#288)

#81 - Make a Github API class
- add class for github api interaction
- only got one method; for raising issues currently

#71 - Suggest an improvement command
Add a suggest improvement command and supporting infrastructure

#122 - Disable revolution buttons when event expires
Simple fix; edit to remove the view (and therefore buttons).

#127 - make &#39;save thyself&#39; validation message ephemeral

#257 - add a help command

#282 - Refactor bsepoints.py
Turn this one large file into lots of smaller files
Edit all the other files to update references to the various classes ([`fb4dc9d`](https://github.com/ESloman/bsebot/commit/fb4dc9d31a0bb10e5cb33b9f45eacc97644b1c2a))

* #283 - Add support for rocket league bets (#284) ([`f1d791c`](https://github.com/ESloman/bsebot/commit/f1d791c31a903be9722718e14fc1ae50f228bde8))

* Fix for database return errors ([`f9e37d4`](https://github.com/ESloman/bsebot/commit/f9e37d4fc84187755335b084d7f1461139c08d33))

* Fix for bet closing errors ([`106689a`](https://github.com/ESloman/bsebot/commit/106689a4905c022908127e0d36d6754c4f40dcab))

* #279 - Fix issue with role rename (#280)

fix for rename was always tagging the king user ([`ee7b6e3`](https://github.com/ESloman/bsebot/commit/ee7b6e3cf2d4d9395b39a95e33b74dc38da303d3))

* Fix mistake with bool declaration (#278) ([`e551bf8`](https://github.com/ESloman/bsebot/commit/e551bf8aa5f1d35ef8052b7f4896f969283bc4c5))

* Various Changes (#277)

- #276 Allow renaming of supporter/revolutionary roles
- #275 Add a &#39;bless&#39; command for the king to bless either supporters or everyone
- fix some potential bugs with pledging and whatnot
- #269 - Change &#39;@silent&#39; to using silent=True parameter
- #255 - Add ruff as a linting option
- #222 - Become less dependent on .env file ([`ce4c0d6`](https://github.com/ESloman/bsebot/commit/ce4c0d614d62fd79024d6d309a959bf589d88acc))

* Bump py-cord[speed] from 2.3.2 to 2.4.0 (#273) ([`67b9f1d`](https://github.com/ESloman/bsebot/commit/67b9f1df7be16d7039a60a05b598a280bd22b186))

* Various changes (#274)

- #269: Began using `@silent` for some messages
- #271: Use Guilds collection for various guild metrics
- #272: Add command to allow &#34;pledging support the King&#34;
- #268: Supporters should get taxed less
- #136: Revolution reminders should be replies
- #80: Revolution shouldn&#39;t trigger when King is young ([`974303c`](https://github.com/ESloman/bsebot/commit/974303ca278937353b73a08a5b8bb3ceeb78a9f1))

* Bump python from 3.11.1 to 3.11.2 (#270) ([`b6a8b48`](https://github.com/ESloman/bsebot/commit/b6a8b48689d9e6bc6dbe755c135fcf2f63bb2523))

* Bump xlsxwriter from 3.0.7 to 3.0.8 (#266) ([`a1649e4`](https://github.com/ESloman/bsebot/commit/a1649e4c511c9646d896da11d49fcd958db9e828))

* #258 - Add further wordle reactions (#263)

- add a reaction for 6/6
- add yellows reaction
- add greens reaction ([`c81e039`](https://github.com/ESloman/bsebot/commit/c81e0392e04a20d35e76aeef4c4d8cae71974efd))

* #261 - Fix BSEddies awards bug (#264) ([`c431fe0`](https://github.com/ESloman/bsebot/commit/c431fe0c8626e2fc74d106c6bb56b0f269920c66))

* #260 - Persist king name in messages (#262) ([`8597f87`](https://github.com/ESloman/bsebot/commit/8597f87c8a09b14d1ddf6d7a6825a9c70a7768b5))

* Bump docker/build-push-action from 3.3.0 to 4.0.0 (#259) ([`0849b40`](https://github.com/ESloman/bsebot/commit/0849b40f29c5c2a37be0f2cf5e7597030b2dd761))

* #240 - Add slash command to enable us to refresh a bet (#256) ([`ab8440b`](https://github.com/ESloman/bsebot/commit/ab8440b749e368f2d2ba360840ea7ea170ce4a01))

* Startup task (#254)

#235 - Startup task don&#39;t trigger every 2 minutes
#235 - finish processing all the guilds before setting finished to true ([`e2ae298`](https://github.com/ESloman/bsebot/commit/e2ae29858c7434e7e6b17cdb4be151fcdcd8d0a9))

* Bump python-dotenv from 0.21.0 to 0.21.1 (#252) ([`7d024a4`](https://github.com/ESloman/bsebot/commit/7d024a4e6660a9b2e0e05ed4ae749284ea4f7efc))

* Bump selenium from 4.7.2 to 4.8.0 (#251) ([`51051a4`](https://github.com/ESloman/bsebot/commit/51051a467235be623d2ae6a8c93ad107cb9eb76b))

* #235 - Add startup task (#253)

- Create a new `GuildChecker` task that runs on startup and subsequently every 12 hours
- Remove most things from the `on_ready` client event
- Make GuildChecker wait for `on_ready` to be done
- Make all the other tasks wait for GuildChecker to be complete too
- Fix some of the logic in startup functions so it works as expected ([`0653fc2`](https://github.com/ESloman/bsebot/commit/0653fc213ad938b36493404d91cb23fcfdb0102a))

* New KING RENAME command (#249)

- add slash command to change king role #206
- add beginnings of guilds Collection for storing guild specific information #79 ([`675e097`](https://github.com/ESloman/bsebot/commit/675e0974608fdb171502ab0fa5a07bf7c79def2c))

* Esloman/misc (#248)

* #245 React to wordle scores
* #203 Include bot&#39;s average wordle score in stats
* #242 Begin readme updates
* #208 Add placeholder logger to stats class ([`7a93159`](https://github.com/ESloman/bsebot/commit/7a93159b04dcd87e968f5f864eaa6e024d076435))

* #183 Wordle solving improvements (#247)

- add word frequency data
- use word frequency data as weightings in random.choices for picking words ([`ec47ee8`](https://github.com/ESloman/bsebot/commit/ec47ee8e51e5bb6db960b23e17ee9489a38d27ed))

* #184 - Refactor selects.py (#246)

- Create selects subdir with __init__
- move selects into their own files within subfolder
- update the various files that relied on those select classes ([`4f8116a`](https://github.com/ESloman/bsebot/commit/4f8116acd5fc8ebc308322672c81428814a28ccf))

* #193 add more trigger_typing (#244) ([`a7dcc55`](https://github.com/ESloman/bsebot/commit/a7dcc556b5e8e01d8718540f06249c1e72c324ed))

* Esloman/various fixes (#243)

* #239 - Fix for perpetual &#34;sending command...&#34;
* #195 - Change bot activity for awards
* #193 - Add trigger_typing ([`455d6ef`](https://github.com/ESloman/bsebot/commit/455d6ef6c1ca2a7e2ce7697e5cd269342feba081))

* Various fixes for a few different issues (#236)

* #172 Add BSE server celebration message
* #182 Change log formatting
* #199 Add plurals to threads/channels as necessary
* #171 - Add possible happy birthday repsonses ([`879a599`](https://github.com/ESloman/bsebot/commit/879a59921b19637d4fdc905699158796be526810))

* Bump xlsxwriter from 3.0.6 to 3.0.7 (#233) ([`6ac4a60`](https://github.com/ESloman/bsebot/commit/6ac4a60c9cda037f7e0a673df29bd3b5c6300ad9))

* Bump docker/build-push-action from 3.2.0 to 3.3.0 (#234) ([`babdb11`](https://github.com/ESloman/bsebot/commit/babdb119aed4e573103a7feda52dd35801769778))

* #192 - disable vally message (#232)

disables vally rollcall if previous wasn&#39;t responded to ([`2652aba`](https://github.com/ESloman/bsebot/commit/2652aba3c3ff0f4466b47d41559dc0e24dcf143a))

* #191 - fix for not joining thread (#231)

Update `on_thread_update` to work with Discord&#39;s thread changes ([`e20fb00`](https://github.com/ESloman/bsebot/commit/e20fb0088f81c8eab9796e237c85551239defd36))

* Fix for #202 (#230) ([`1a7641a`](https://github.com/ESloman/bsebot/commit/1a7641a21990753208d13c4090762edda318b63f))

* Remove guild restriction for messages #225 #229

* #225 Remove the guild ID restriction ([`86640f4`](https://github.com/ESloman/bsebot/commit/86640f449d751ed43b05810f97a801d36d3e7b33))

* Bump docker/metadata-action from 4.2.0 to 4.3.0 (#227) ([`a52cada`](https://github.com/ESloman/bsebot/commit/a52cadae2b3dbba24486dc098d506a2daafc1293))

* Bump requests from 2.28.1 to 2.28.2 (#226) ([`d41280d`](https://github.com/ESloman/bsebot/commit/d41280d5052e4468bf5986510965ebe435640382))

* Message edit debug #225 (#228)

- Add some debug information for message edit ([`4c110a8`](https://github.com/ESloman/bsebot/commit/4c110a8f5bbbb77c77a616d96ce321dacb06c1ad))

* Docs updates (#224) (#201, #16)

* Update a load of documentation
* Add some doc strings
* Move some stuff around
* Readme update ([`f4b6211`](https://github.com/ESloman/bsebot/commit/f4b621148fa744454a3e8343c33700156012d935))

* Add issue templates ([`78660ea`](https://github.com/ESloman/bsebot/commit/78660ea8d1f6708b45c7f357dada9f8745ce4b29))

* Update README.md

Update README to be a bit more generic ([`04c7b20`](https://github.com/ESloman/bsebot/commit/04c7b20f4be57b80326909f6c8a7b8573dbf742e))

* Update README.md

Adding some shields and update badge urls ([`ec90dd7`](https://github.com/ESloman/bsebot/commit/ec90dd7aaeff88d3e87c861e9b185f69464c751a))

* Bump py-cord[speed] from 2.3.1 to 2.3.2 (#220) ([`6bb2468`](https://github.com/ESloman/bsebot/commit/6bb246868887240264edae1c370fa379086490e8))

* Bump pymongo from 4.3.2 to 4.3.3 (#218) ([`f2c71cc`](https://github.com/ESloman/bsebot/commit/f2c71cc8b6310b570dabf0e0d4164858ee1e4a04))

* Bump actions/setup-python from 2 to 4 (#216) ([`7492c1d`](https://github.com/ESloman/bsebot/commit/7492c1d769ce9b27c3aef37b37639020930e82c4))

* Bump docker/login-action from 1.10.0 to 2.1.0 (#214) ([`66f59fe`](https://github.com/ESloman/bsebot/commit/66f59fec79a637e9a10451449b3b832aaef6748f))

* Bump docker/build-push-action from 2.5.0 to 3.2.0 (#215) ([`9bf4407`](https://github.com/ESloman/bsebot/commit/9bf4407cfab03ffe1125dc80dbd6c78e1d640a2f))

* Bump xlsxwriter from 3.0.3 to 3.0.6 (#219) ([`a68466b`](https://github.com/ESloman/bsebot/commit/a68466bc9f5aa28e5d91f6e6e0bffb3222d48e78))

* Bump docker/metadata-action from 3.3.0 to 4.2.0 (#213) ([`782ea2c`](https://github.com/ESloman/bsebot/commit/782ea2cd36153bcbd0a8f52f6228b686a30c6f1d))

* Bump python from 3.11.0 to 3.11.1 (#212) ([`b64110a`](https://github.com/ESloman/bsebot/commit/b64110a1e9c2a849b7cd3e8373381561c771504e))

* Enable dependabot for managing versions

- added dependabot.yml file
- update requirements.txt
- added environment to workflow ([`1c216f0`](https://github.com/ESloman/bsebot/commit/1c216f02ac970fe9010fbe15a1b020c6b51e8624))

* Trigger wordle if we missed it (#210) (#211)

Changed the wordle logic so that it&#39;s less dependent on a particular time ([`d3a46eb`](https://github.com/ESloman/bsebot/commit/d3a46eb18698bf920d249eed9af4b7420cea2d82))

* Switch to using css selectors (#207) (#209)

This removes the reliance on specific class names for certain elements and hopefully means that we&#39;re a bit more resilient for when Wordle gets updated and the randomly generated class names change.
Additionally (#201), remove some files that aren&#39;t used anymore and (#208), add the placeholder logger object we can use throughout the codebase. ([`cc8a408`](https://github.com/ESloman/bsebot/commit/cc8a4085e6b5e78ea5048144b5bc3d702f34e6d7))

* Hotfix for stats (#198)

- Fixes #196, #197, #200
- Make keys strings
- Fix date year being incorrect
- Make year/month optional kwargs for stats documenting ([`bf58e89`](https://github.com/ESloman/bsebot/commit/bf58e897a97ad963b9daed8dc7f682461524a9fd))

* Add a hotfix for wordle threshold (#194)

Ensure that users doing `/wrapped22` will get a wordle result if they&#39;ve done _any_ wordles this year by bypassing the threshold. ([`44943d3`](https://github.com/ESloman/bsebot/commit/44943d3d18ebe1b20c46f5e9efa5037e0bbba94e))

* Fix an issue with the emoji stat for /stats and /wrapped22 (#190)

* Fix an issue with the emoji stat for /stats and /wrapped22
* Fix a flake8 typing issue ([`95d1806`](https://github.com/ESloman/bsebot/commit/95d18069267c80795c95398f3df777c1316d32bb))

* Add a share button for Wrapped22 (#188) (#189)

- Added a wrapped view
- View button shares the message publicly ([`dadedc5`](https://github.com/ESloman/bsebot/commit/dadedc5691042abd04391c56a55e97f5f0c1503f))

* Awards improvements (#186)

* Add some minor improvements for awards
* Add most popular server emoji for Wrapped22 ([`6a0cb07`](https://github.com/ESloman/bsebot/commit/6a0cb0784d447b78cac463a341aebe0fad444a6e))

* Adding BSE Wrapped 22 (#185)

Add initial logic for Wrapped 2022:
- added a new stats slashcommand with a wrapped22 function (#147)
- makes gathering user stats a bit more dynamic for wrapped and future work (#137)
- fix a lot of errors if stats didn&#39;t have data (#108) ([`69ef77f`](https://github.com/ESloman/bsebot/commit/69ef77f9e7a930d737db89cc41715bb09ac26f89))

* Wordle solving #176 (#177)

- Solve the wordle ourselves using selenium and chrome driver
- Words are selected randomly based on the previously entered word
- Construct the shared text ourselves
- Retry a few times if we fail (due to the randomness of our selections)
- Log wordle attempts to the DB ([`656f57a`](https://github.com/ESloman/bsebot/commit/656f57a22d1eaab30a45e98408efaf09f1743c34))

* 2.1.0

Closes out feature set for 2.1.0.
Changes:
- Added more awards and stats for BSEddies awards (#159)
- Split award messages if they&#39;re over 2000 chars (#160)
- BSEddies awards; runners up are logged to DB (#165)
- Added additional tasks for holidays (#166)
- Added bot politeness for when being thanked (#168)
- Implemented bet reminders for bets that live for more than ~2 days (#131)
- added more type hinting (#129)

Bug fixes:
- `/create` not deferring properly (#145)
- wordle reminder triggers when a user fails their wordle attempt (#161) 
- bot too eager to say &#39;you&#39;re welcome&#39; (#173)
- stop other bots (craigbot, patchbot, etc) from winning BSEddies awards (#159) ([`445d288`](https://github.com/ESloman/bsebot/commit/445d288f12621b2f6e7e5dfd9dc184cf616dd7ec))

* Eagerness fixes (#174)

* Fix eagerness with &#39;you&#39;re welcome&#39; (#173)
- Use regex matching with word boundaries
- Don&#39;t reply to self messages ([`f529bda`](https://github.com/ESloman/bsebot/commit/f529bda93c5984a5aa1ed4318ff28d7c96c3ced3))

* Add Celebrations task (#166) (#170)

- Added basic framework for celebrations
- Add message for Christmas
- Add message for NY day
- Add message for bot birthday ([`3c70f9b`](https://github.com/ESloman/bsebot/commit/3c70f9ba0e903f7d29db9bf9b294b5230b664757))

* Simple thanks (#168) (#169)

Add very primitive way of replying to users that thank us ([`6507f75`](https://github.com/ESloman/bsebot/commit/6507f754bfcc7f42877a16d54e489c43dceade16))

* BSEddies Awards (#167)

* BSEddies Awards (#165)
- Log stat dicts to the DB

* BSEddies Awards (#159)
- add the single minded award
- add diverse portfolio award
- add some debug for some other errors ([`03a7446`](https://github.com/ESloman/bsebot/commit/03a7446cc9e0019fb519d18f8231625e31bdf18e))

* BSEddies Awards Updates (#164) (#159, #160)

* Updates for wordle logic
- change wordle eddie values
- make sure eddie gain class won&#39;t crash in the morning

* BSEddies Awards (#159, #160)
- Add message splitting in case we hit the char limit (#160)
- Add server emojis created for the year (#159)
- Add edited messages award (#159) ([`52bd8f7`](https://github.com/ESloman/bsebot/commit/52bd8f776ef5f758b86ba6146fc7a83133fad7ca))

* Update wordle logic (#161) (#163)

- Amend regex so that we account for failed attempts
- Don&#39;t remind the bot to do the wordle, regardless if it&#39;s done it or not ([`6a50f23`](https://github.com/ESloman/bsebot/commit/6a50f2366d5112de927d6d97136b8e6c978987b0))

* Edited messages (#158)

* Make sure that we don&#39;t add edits for embeds ([`f5fbb4f`](https://github.com/ESloman/bsebot/commit/f5fbb4ff100467c78949a80771e553127fb81285))

* Make sure we pass kwargs when their value is &#39;False&#39; to the method ([`3b3f652`](https://github.com/ESloman/bsebot/commit/3b3f6523753ea12097f0fb56135e288767ee930b))

* BSEddies awards (#143) (#157)

BSEddies awards (#143)
- Add server owner as a monthly award as well
- Fix a few niggles with how vc time is displayed in eddie breakdown ([`a9f677e`](https://github.com/ESloman/bsebot/commit/a9f677e51d6b0a985c62c8984025607e39b9b6e4))

* Fixes (#156)

- fix for archived threads ([`449fcaa`](https://github.com/ESloman/bsebot/commit/449fcaa65d2d1db5c29c9cdf0cdfb366aa2554fc))

* Various fixes (#155)

- thread_create sets uses message ID as message ID
- fix issue with awards text
- make sure we don&#39;t send awards/stats to debug channel
- go back to normal installation of pycord (#154) ([`1d8d87c`](https://github.com/ESloman/bsebot/commit/1d8d87cd50d101f6a4a6d6ca1628041b7ab242d9))

* Wordle reminder (#153) (#151)

- Commit changes made in prod to get it functional.
- Enable actual reminder sending ([`6665409`](https://github.com/ESloman/bsebot/commit/6665409a74bcd14783182a4e4d754ceec098a54d))

* Wordle reminder (#151) (#152)

* Wordle reminder (#151)
- Add wordle reminder task in debug only atm
- Fix errors with message edit ([`43e423c`](https://github.com/ESloman/bsebot/commit/43e423c2b45e7095b56f65715f6de1e41029e131))

* Predict improvements (#150) (#100, #112)

- predict should show me everything now
- daily message should show taxed eddies correctly and general tax info ([`830fb29`](https://github.com/ESloman/bsebot/commit/830fb29f5b264da1dbe133ee880ccf6db3086538))

* Don&#39;t care if message_type is application command ([`293615b`](https://github.com/ESloman/bsebot/commit/293615b91e10083830d455e40fcad2ee5a1b4cc3))

* Leaderboard should show who refreshed it (#103) (#149)

* Leaderboard should show who refreshed it (#103)
- Leaderboard shows name of user who triggered slashcommand or pressed button
- Highscore now does the same ([`ed6d8a3`](https://github.com/ESloman/bsebot/commit/ed6d8a3a157d9ebf11e1327b1fe98fdb296e2d6a))

* Fix errors (#148) (#145)

* Fix issue with &#39;sending command&#39; message persisting (#145)
* Ignore messages not in channels we care about ([`1a14eaf`](https://github.com/ESloman/bsebot/commit/1a14eaf975f0934a1c1ed64e8b0f96838ed4a8f1))

* Fix issue with &#39;sending command&#39; message persisting (#145) (#146)

When using the `create` command to create a bet - the &#39;sending command&#39; ephemeral message would persist despite the bet being created. This resolves that issue. ([`0114440`](https://github.com/ESloman/bsebot/commit/011444089e8b1642edbc7cb2393887d4f8a7fddc))

* Handle on_message_edit events (#140) (#144) ([`e78b2ae`](https://github.com/ESloman/bsebot/commit/e78b2ae97a495f3d1e84f6df6a004f3238909cf4))

* BSEddies awards (#143)

* Various improvements for BSEddies Awards:
- Add emojis for stats/awards (#142)
- Add most replies/replied to awards (#115)
- Finalise thread stats and awards (#132)
- Add server owner award (#139)
- Add quietest channel/thread/day (#116)
- Add support for filtering out deleted channels for &#39;quietest_channel&#39;
- Increment max_messages parameter (#141)
- Add support for checking if messages were sent in a VC or not (sigh) ([`d2ef01d`](https://github.com/ESloman/bsebot/commit/d2ef01ddb20688420b1b625e995bac249daf2c7f))

* Bseddies awards (#138) (#132)

* Add busiest thread stat (#132) ([`5166d94`](https://github.com/ESloman/bsebot/commit/5166d943ad822d9bfae8a83cb94c2ba0d40a5041))

* Add bet reminders (#131) (#135)

For longer bets, add a reminder message twenty four hours before it expires. ([`cd83ca7`](https://github.com/ESloman/bsebot/commit/cd83ca71e3fe05c030a2330f0142ff6e32049315))

* Better threads handling (#132)

- Track whether a message is threaded or not
- Add thread flag to dicts ([`3924efb`](https://github.com/ESloman/bsebot/commit/3924efb4031ae67c61a3532aa0874e5dcf3bdbb2))

* BSEddies awards and other fixes and improvements (#133)

Various changes to the awards/stats and some other improvements along the way.

- Add some VC stats (#117)
- Allow King to be counted properly (#126)
- Wordle stat now excludes those that haven&#39;t done at least half the wordles (#118)
- Add a most popular server emoji stat (#114)
- Add dataclasses and type hints for DB dics (#129)
- Fix an issue with revolution formatting (#104)
- Refactoring to reduce some complexity
- Various bug fixes to do with message caching ([`38d3c02`](https://github.com/ESloman/bsebot/commit/38d3c022cb57f171c25b6336fa77c90d5599a55e))

* Bug fixes (#119, #120, #104) (#124)

- Stop pook from breaking revolution event; don&#39;t allow users to use the &#39;Save THYSELF&#39; button 
- Allow users to switch sides during a revolution event
- Fix a formatting issue with revolution text ([`9955221`](https://github.com/ESloman/bsebot/commit/99552214ff6476357b730c0a54ab11ed0480ee4a))

* BSEddies Awards (#76 #77) (#113)

- Refactor to add in &#39;AwardsBuilder&#39; which builds the stats and awards message for both monthly and annually. Removes duplicated code from monthly and annual tasks and will make future updates easier.
- Add additional stats and awards
- Add &#39;Annual awards&#39; task which will trigger on the first of each year
- Add some extra tidbits to some of the existing stats ([`77991b9`](https://github.com/ESloman/bsebot/commit/77991b956e11dfffa4da80db044aa78010ffd2a3))

* Track time spent in voice channels (#18)

- Add the framework for tracking users in VCs
- Add giving them eddies for doing so ([`f453119`](https://github.com/ESloman/bsebot/commit/f453119c38f806ef294bed7b6cc9a4479b84df34))

* BSEddies Awards updates (#105)

- Add twitter addict award
- Add some more information
- Add some fixes for posting data to DB
- Change method of building to get speed enhancements for pycord ([`037ddd0`](https://github.com/ESloman/bsebot/commit/037ddd0782b846ea9a1d336890c7a2c84408b021))

* Implement Flake8 (#101)

- Add `flake8` linting action to github for commits and PRs
- Add `flake8` configuration file
- Fix the all the linting issues to conform with PEP8 and tidy up the repo ([`cc01dbf`](https://github.com/ESloman/bsebot/commit/cc01dbfc86d57ac329922cd1bd838fbd30c6b4c5))

* Further refactoring

- Move all tasks into sub-directory
- Fix bug with daily salary and threads
- Refactor some long lines ([`c5235e9`](https://github.com/ESloman/bsebot/commit/c5235e929e54819da11a574169f604965090c76f))

* BSEddies Awards and other updates

- Update python version to 3.11
- Update build process to allow `py-cord` to be installed on 3.11
- Some major refactors to remove redundant code and tidy up
- Enable the BSEddies awards! Stats and prizes for our good members - coming soon. ([`9f94544`](https://github.com/ESloman/bsebot/commit/9f94544d7a52ccfb9ba225180476246a3e164a31))

* Refactor and upgrade

- Remove uneeded importants
- Fix build to pull dev version for pycord from github for python 3.11 support ([`f67b9c8`](https://github.com/ESloman/bsebot/commit/f67b9c8873b581c305a300b31e9ec45b1da0de60))

* Refactor (#96)

* Add some more type hints
* Some more refactoring work ([`95a4e4f`](https://github.com/ESloman/bsebot/commit/95a4e4f0f0846035fab111abcd0693a5fbdc2690))

* Bseddies awards (#95)

- Refactor the stats a little
- Add participation stat
- Add the awards to the DB for future use ([`5fc70ea`](https://github.com/ESloman/bsebot/commit/5fc70ea67778a4a9cdc43b59584e7793183319b5))

* Bug fixing and tidy up (#94)

- Resolve #93: Cancelling a bet still allowed bets to show up in `/pending`
- Resolve #85: Revolution event not showing supporters/revs correctly
- Resolve #92: Update docker image to use Python 3.11 (and resolve build issues caused by this)
- Simplify some dependencies and update versions
- Remove some unused files and packages ([`7945bba`](https://github.com/ESloman/bsebot/commit/7945bba162b0cb1c0348fb4dfe30e86e71c3666a))

* Major refactor (#91)

- Create folders for client event classes, slash commands and views
- Each command, event, and view is a separate file
- Change docs accordingly
- Remove beta mode
- Move the commands sync
- Remove all print statements and replace with logging
- Add more logging to the on_ready event on startup
- Make sure to add more type hints
- Actually add emoji and sticker event listeners ([`da8e468`](https://github.com/ESloman/bsebot/commit/da8e46852d2d5f34c1e1d2a217e35f0a7738bc74))

* Disable auto-syncing to mitigate API rate limits and manually sync on startup (#89) ([`debcdee`](https://github.com/ESloman/bsebot/commit/debcdee6e8239e773f19a61592f53d1e56ae4a87))

* Add the start of the monthly `BSEddies Awards`! Featuring stats and prizes.

Add functionality to trigger a monthly &#39;stats&#39; message for the server. This triggers on the first day of a month and provides stats on the previous month. There are also some stats that can be &#39;won&#39; - these are the BSEddies Awards. Users can win these and will gain a small eddie prize.

- Add awards task
- Add stats gathering and caching class
- Add supporting enums and constants for needed vars ([`9d5a3cf`](https://github.com/ESloman/bsebot/commit/9d5a3cf95837c92b058006e4fdf942e3d628e570))

* Docs update (#88)

* Update docs ([`80cb210`](https://github.com/ESloman/bsebot/commit/80cb2103482ce31556a73a445394e294e57065e2))

* Docs update (#86)

* Add some docs
* Add a suubfolder for tasks ([`2d5c823`](https://github.com/ESloman/bsebot/commit/2d5c823f1c62ea1d79767b5245dc992575a3d418))

* Merge pull request #78 from ESloman/compartmentalise

Fix some startup errors on fresh installs ([`dbe2386`](https://github.com/ESloman/bsebot/commit/dbe2386e80259967b36fd233e0813636cad67d60))

* Fix some startup errors on fresh installs
- Allocate some tasks to prime server only
- Fix for when no hash doc in local deployment ([`2a01aa2`](https://github.com/ESloman/bsebot/commit/2a01aa237d73602a74f02984c912940f9d478446))

* Repo admin updates
- Updates to readme.md and contributing.md
- Updates to .gitignore
- Updates to requirements.txt ([`0a57eed`](https://github.com/ESloman/bsebot/commit/0a57eed1a0c82cc580d606fd68d038c8c1741c67))

* Tweak for spoiler thread task

- Stop bot posting in spoiler threads that have finished airing ([`ab52968`](https://github.com/ESloman/bsebot/commit/ab52968cefeb39c1a74b2c4236cb11cc40fe8daa))

* Modify some of the reminder messages for revolution events ([`846ee49`](https://github.com/ESloman/bsebot/commit/846ee494ca7e992f64ba144446dfd6dc5fbae767))

* Actually show usernames in revolution event for revs and supporters rather than user ids ([`55b0621`](https://github.com/ESloman/bsebot/commit/55b06214454cb5c5b098a8733905209d8b267267))

* Fix startup error ([`a765e56`](https://github.com/ESloman/bsebot/commit/a765e56606333fd39b45d392cbd46157d933edf8))

* Increase wordle time variance ([`f527044`](https://github.com/ESloman/bsebot/commit/f5270441f31fb2e1584b76f165fc95f937df8958))

* - Fix issue when user tries to place bets when they have 0 eddies
- Fix issue with bet place when the eddies/half eddies the user has is equal to a value already in the options list ([`2351359`](https://github.com/ESloman/bsebot/commit/2351359d07c5def96f2dadc0f85993dae105025a))

* Disable some event intents as those events aren&#39;t used. ([`06b0dfb`](https://github.com/ESloman/bsebot/commit/06b0dfbffe5fd717d59696d9a408d955fda8d084))

* Init bet views in threads

- Ensure that bet views in threads are re-initialised upon startup
- Make sure that pending bet views are also re-initialised correctly ([`8fc00b3`](https://github.com/ESloman/bsebot/commit/8fc00b38f3be6797e6ca89118aae3f6f75d7001c))

* Fix issue with revolution event - where the KING spending eddies to reduce the chance incorrectly states how many eddies they spent ([`5ca09e7`](https://github.com/ESloman/bsebot/commit/5ca09e74870cf54c8cae129e151d661564444edc))

* Fix interaction bug with trying to cancel a bet owned by someone else ([`61913c5`](https://github.com/ESloman/bsebot/commit/61913c525d18c8b15b0bf72881b58792ce882bf2))

* Fix for reactions in thread messages

- Fix error for reacts in thread messages causing errors ([`842ecf5`](https://github.com/ESloman/bsebot/commit/842ecf5c13c8548fb935cb09287aedc7b0505aa8))

* Enable update message

- Finalise code for sending update messages ([`62582ca`](https://github.com/ESloman/bsebot/commit/62582ca0b6ebbe0f51dc91a49c0653a752fdb47e))

* Add &#39;Cancel bet&#39; button

- Adds a &#39;Cancel&#39; button to bets to remove them from play. Everyone gets their eddies back with no penalties. ([`53f78d2`](https://github.com/ESloman/bsebot/commit/53f78d295f5e49ae6507e2f896834318d79dce7a))

* Some bug fixes

- Remove redundant line from Dockerfile
- Fix ordering of logging to prevent an error
- Wrap git stuff in try/except ([`4501fcd`](https://github.com/ESloman/bsebot/commit/4501fcd88aff98426a2e588ada45f758adf133ba))

* New daily vally message

Add the &#39;fat ones&#39; message variant to daily valorant messages ([`e862231`](https://github.com/ESloman/bsebot/commit/e862231da7a71c00ed57ce98309c1d7aa97cfd10))

* Automatic update messages

Add logic and supporting infrastructure for posting updates automatically on a restart ([`8e3c023`](https://github.com/ESloman/bsebot/commit/8e3c023f8eeda303d53ef74ce349de864cb65ca6))

* Revolution event update

- Add button for the King that allows them to reduce event chance for a large cost of eddies
- King will no longer change during a revolution event, regardless of who has the most eddies ([`5486ec4`](https://github.com/ESloman/bsebot/commit/5486ec476f8d4f2cd35df8c9a64ca831f8e965c9))

* Improvements to autogenerate command

- add timeout select to autogenerate
- random bet selection is smarter: will actually pick the right number with validating the conditions
- fix a bug with some particular bet types
- tidy up some code ([`a811634`](https://github.com/ESloman/bsebot/commit/a811634935abaea5b9e2a5350d4a856af4f04070))

* updates for bets ([`933e6a4`](https://github.com/ESloman/bsebot/commit/933e6a412cb122d65e52b1ecc5e385cc474d4098))

* fix ([`f285832`](https://github.com/ESloman/bsebot/commit/f2858326b987849b32e7443f4bd17c0f6418709d))

* fix for predict ([`69da95e`](https://github.com/ESloman/bsebot/commit/69da95e2568b517025e1100945c31e2ed842d706))

* Fix issue with the &#39;fill&#39; type bets ([`fb9b7b9`](https://github.com/ESloman/bsebot/commit/fb9b7b9b76077abf4df3b1f8e7b1b0a29fb6e0e1))

* cd into the git dir before doing git things ([`c84d7d9`](https://github.com/ESloman/bsebot/commit/c84d7d9888dc19ccfd458b4481de01cd65307ff1))

* Change method of git_hash selecting ([`0e81246`](https://github.com/ESloman/bsebot/commit/0e81246884e5b26f9a375b9ae5f6e177bf5ab6d5))

* Adding required bits to workflow and Dockerfile for auto update messages ([`a8af9ef`](https://github.com/ESloman/bsebot/commit/a8af9ef65b98e01a5d875ba58c8ad477890907e2))

* Add some more vally options ([`4d98b07`](https://github.com/ESloman/bsebot/commit/4d98b0724b28c5e075e43c43171d6c5c90381e1f))

* Remove redundant imports ([`3eadb68`](https://github.com/ESloman/bsebot/commit/3eadb68a5acb49695061bdbf4cc0ee158d0af46b))

* Various changes:
- added more randomness to bet odds
- bets have lower returns if everyone voted for winning outcome
- bet winnings are now taxed
- notification in the bseddies channel when a king changes
- notification in the bseddies channel when the tax rate changes
- remove all custom_ids from bet views and selects to prevent fuck ups
- add some logic to autogenerate that will fill options with those in the voice channel
- add the logic back to autogenerate that will only select a bet if the requirements are met ([`048dd6a`](https://github.com/ESloman/bsebot/commit/048dd6ac97a688d279aaba27856d3fcc85cac1ed))

* Tax bet winnings

Some changes to tax bet winnings the tax rate too
Only taxing the actual winnings though - so user always gets what they bet back plus the taxed bet amount
Bet winnings modifiers are now randomised a bit to give a bit more spread on the winnings (pretending there&#39;s variable odds) ([`6017fa5`](https://github.com/ESloman/bsebot/commit/6017fa565893fcf08eb75db004cea5ea2850d882))

* fix for already deferred error) ([`d9a7e10`](https://github.com/ESloman/bsebot/commit/d9a7e106661d89d75b27a88cde404835a3aaeab3))

* Sort bet titles in the right place this time ([`b808669`](https://github.com/ESloman/bsebot/commit/b80866900e46fe47ae18e1e11da6e6a1f2501c4e))

* Sorting bets by title ([`7a4ab0c`](https://github.com/ESloman/bsebot/commit/7a4ab0c7652f482213a96d89717ba3daf12654d6))

* Get the update op the right way round\nAdd message for trying to revolution more than once ([`c5e2bfb`](https://github.com/ESloman/bsebot/commit/c5e2bfb4265950fe78bcc2e0450f867477a34c6f))

* fixed issue with tax rate and added more emojis ([`7660fd8`](https://github.com/ESloman/bsebot/commit/7660fd8f8d4f7a4c7ce200c83876ae023cc8f878))

* fix more errors ([`ce17c06`](https://github.com/ESloman/bsebot/commit/ce17c0663ff1e39d4276976c5ed0b548af52d402))

* fix bet ids ([`b3803c7`](https://github.com/ESloman/bsebot/commit/b3803c77041a11deab5d44f312e5d69f2b6de97a))

* Add some debug logging ([`1c60a89`](https://github.com/ESloman/bsebot/commit/1c60a8961e4bfde6899ef11fe0886b6b1a0f4dd8))

* fix random autogenerate ([`073e555`](https://github.com/ESloman/bsebot/commit/073e555d73b48a91e671c018e40727e67c3ef0db))

* fixes for revolution event ([`d163da4`](https://github.com/ESloman/bsebot/commit/d163da47e38f776474bf0ae430692168ad709cd0))

* Add framework for tax rate ([`2920c38`](https://github.com/ESloman/bsebot/commit/2920c380dd32a31c686762fef4c27c4b8aca359f))

* Fix emojis ([`6908335`](https://github.com/ESloman/bsebot/commit/6908335f0c351b803d544758a636f0dacb4fe7a1))

* Add some emojis ([`3022edf`](https://github.com/ESloman/bsebot/commit/3022edfa2398a0df1e27352280ed01a805a57cbd))

* Fix issues with autogenerate not triggering
Fix issues with close_bet messages not getting edited ([`5b6d3c8`](https://github.com/ESloman/bsebot/commit/5b6d3c88dea26ca49cca50b7a95f3ae81befc736))

* Change an await to a get ([`f1cfeb7`](https://github.com/ESloman/bsebot/commit/f1cfeb752c4f3704e97ffa43eb3b488b00ec4560))

* Add fix for on_ready event error ([`52c8b98`](https://github.com/ESloman/bsebot/commit/52c8b98ba9982d5ee5c570a5483515461fe47964))

* Add ephemeral parameter ([`62c03f3`](https://github.com/ESloman/bsebot/commit/62c03f3012326561936ca9aec750d9e9d8d84f33))

* Add logs of logging to the thread mute task to diagnose the issue
Use the bot&#39;s wordle score when working out wordle winner ([`856e07f`](https://github.com/ESloman/bsebot/commit/856e07ff08c73449fee5ed3f7d8d0b8d84796c77))

* Re-enable wordle for next restart ([`f2c21c1`](https://github.com/ESloman/bsebot/commit/f2c21c123665e26634ee2526d6e17fe8e42e537a))

* Add logic for actually triggering auto bets
Some tidy up
Disable wordle task for now ([`0e127fc`](https://github.com/ESloman/bsebot/commit/0e127fcad5ac5f89225cb030a4b97627fba92e48))

* A few new features and major updates and minor updates:
- add spoiler thread task
- bet winners now get a share of bet loser eddies that were bet
- Beginning adding the autogenerate slash command back in ([`4d6ac13`](https://github.com/ESloman/bsebot/commit/4d6ac13dd3a4cfebfb2820ba283d10ed448dc69f))

* Tweaks to tasks ([`b577e92`](https://github.com/ESloman/bsebot/commit/b577e922ed290c3132b2c5ddf61615ad1f1beb3d))

* Add some logging to wordle task ([`1d7529c`](https://github.com/ESloman/bsebot/commit/1d7529c91e8444f8a8d37f2984a7d1b6e4046cdc))

* Actually set timezone automatically ([`5b42c0c`](https://github.com/ESloman/bsebot/commit/5b42c0c89432c606ef175c1ba6dc77aef27fa0e3))

* Add daily wordle task ([`f1fa5a3`](https://github.com/ESloman/bsebot/commit/f1fa5a319f7755bfd3742de00ce659767a7a0aba))

* Fixes and improvements after day one:
- Users can only support/overthrow once
- Make sure the keys are created in the DB object
- Fixes for if we need to restart the bot during an event
- Cap the chance value publicly
- tidy up some messages
- make sure bet timeout message is cast to lowercase
- added task for daily vally message ([`c9ef5b4`](https://github.com/ESloman/bsebot/commit/c9ef5b4e02d37b5d68a8d5e0ec1f391d8537e823))

* Fixes for event ([`d4f64bf`](https://github.com/ESloman/bsebot/commit/d4f64bf95562e08030916590f7f0fe76c54feff5))

* Add no timeouts for bets
Try to add active views on startup for all active bets
Make sure switching sides in revolution event doesn&#39;t mess with the chances too much ([`a623f0c`](https://github.com/ESloman/bsebot/commit/a623f0c91ae2b40b42e1e8eaa36c2afb914a1a2a))

* Create the bet view a little earlier ([`bb6de17`](https://github.com/ESloman/bsebot/commit/bb6de17743e8bcded7e077840ae4daaf52c6996b))

* Added custom ids to some of the views
Add creating a new view when successfully placing a bet ([`fbf3753`](https://github.com/ESloman/bsebot/commit/fbf3753c4b80f7224c8e4c918f8973caa6654570))

* Add missing &amp;&amp; ([`8d49316`](https://github.com/ESloman/bsebot/commit/8d493167a4642003b682a593b0353c0c6540f571))

* Fix issue for not being able to bet on bets in threads
Make leaderboard view persistent ([`1769aa4`](https://github.com/ESloman/bsebot/commit/1769aa4849f8b56c64c50ae367d7b4fa8b69cf57))

* Fix for setting timezone from dockerfile ([`b1ded5f`](https://github.com/ESloman/bsebot/commit/b1ded5f071f5ae40ace278d6a191d9914ded5a42))

* Hopefully add correct timezone to dockerfile
Fix eddiegains error ([`dad70b6`](https://github.com/ESloman/bsebot/commit/dad70b6ad3ecc23c6d775a341bfb7bd4c6c387ad))

* Fix typo ([`90b64cd`](https://github.com/ESloman/bsebot/commit/90b64cdb83e3cb2dceada899cb960ded39713f0f))

* Making sure rev task actually triggers
Make eddie gains real
Some tidy up ([`8baec5e`](https://github.com/ESloman/bsebot/commit/8baec5e0041aa59122b1cf36ee70afe5ea6eb6ab))

* Fix some type hints
Change eddie gains back to a different loop type ([`f5f4f82`](https://github.com/ESloman/bsebot/commit/f5f4f82a2a732d656da93fe8500fb42c222f12d4))

* Change time to 6:15 and try again ([`077809f`](https://github.com/ESloman/bsebot/commit/077809f3267e5a32620276595c359730628eb812))

* Let predict function correctly by passing in the `days` parameter ([`02415a9`](https://github.com/ESloman/bsebot/commit/02415a992000a68101ff5d1c6d7ca8c92a5dbbbb))

* ctx.defer needs to have the ephemeral bit ([`4cb4876`](https://github.com/ESloman/bsebot/commit/4cb4876a08227e669fcbb00f7b92f6de69efad8e))

* Fix issue with tuples on eddie gains ([`ba2f1a3`](https://github.com/ESloman/bsebot/commit/ba2f1a39837180cf6de1026772e73c17bc7f9a0d))

* Make sure debug mode is turned OFF
Make sure giphy token is set in the ENV properly
Floor the taxed amounts ([`e47fe2e`](https://github.com/ESloman/bsebot/commit/e47fe2e609fa59c43a81f20184c0281afa8529cc))

* Add persistent view for revolution event ([`7cbe56e`](https://github.com/ESloman/bsebot/commit/7cbe56e9c1e696ad2832915cc7dbfb4ece002a58))

* Large update: #61 #62 #63 #68 #69 #75
- Added supporting work for custom emojis and stickers
- Added new revolution event framework (just need to add variable tax rate)
- various tweaks to do with replies and stuff
- Lots of other minor updates ([`f6beef3`](https://github.com/ESloman/bsebot/commit/f6beef397b552e67f8323e525f5c4d86bf33e662))

* Only show users who have ever received/used eddies in leaderboards ([`717e20a`](https://github.com/ESloman/bsebot/commit/717e20a65b6e0d6278bafd9467953eb8c8347190))

* Add basics of activity and fix bug with eddie amounts
#63 #74
Bot now say it&#39;s listening to conversations and issue with amounts is resolved ([`4669435`](https://github.com/ESloman/bsebot/commit/4669435bd551c16ed6398fc881da6350e0c7d1c8))

* Fix bug with placeholder outcome names

Part of #63 
Fix a bug where having only one bet available to place/close will cause placeholder values to appear for outcomes rather than actual outcome values. ([`09b63f4`](https://github.com/ESloman/bsebot/commit/09b63f4f7b8f2ec16601e91b73f5eca54e1d9202))

* Update Dockerfile #64

Remove ls debug commands and move all RUN commands into one ([`854d1b8`](https://github.com/ESloman/bsebot/commit/854d1b80e3a5749b95b46c606d8e2f690e3b834d))

* #70

Try tagging the image with sha instead ([`ec6dacd`](https://github.com/ESloman/bsebot/commit/ec6dacdd67c78401bc6357135202b7d5f8a29c43))

* #64 #65
Missing a &#39;.&#39; ([`bf1f751`](https://github.com/ESloman/bsebot/commit/bf1f7518a25df261cf2d401ad12bfd75e041652f))

* #64 #65 #63 #61
Some fixes for a couple of bugs when there are no bets
Remove more redundant code
Update docker deployment slightly ([`0cee6d1`](https://github.com/ESloman/bsebot/commit/0cee6d16292dd8ca07a7fa7a0d4890459214c83b))

* #64 #65
Tidying up of classes and fixing some errors with deployment ([`37f314e`](https://github.com/ESloman/bsebot/commit/37f314efd419382d7f4784abbaa54ccce8d74a15))

* #64 #65
Change directory copy ([`9d8d354`](https://github.com/ESloman/bsebot/commit/9d8d3540f499ae49a5437fd95b1c96589b7633a5))

* #64 #65
Don&#39;t build from slim image - use full image ([`afa8075`](https://github.com/ESloman/bsebot/commit/afa807595c1885bc4306bf24b0c983ff73cd8250))

* #64 #65
Correct dockerfile and actions file ([`da82951`](https://github.com/ESloman/bsebot/commit/da8295164c5a521ce7694d0cc359b309dd56a650))

* #64 #65
Update dockerfile pip install
add build-args to workflow ([`a7af781`](https://github.com/ESloman/bsebot/commit/a7af781a94d749774243a9ccee6bd0726c0972d0))

* #64 #65 adding dockerfile ([`1908e1b`](https://github.com/ESloman/bsebot/commit/1908e1b9c4a39090b293669f15f3482cb05b4152))

* #64 #65 - First attempt at using a workflow ([`f7c855f`](https://github.com/ESloman/bsebot/commit/f7c855f9e89f4a1e46008de42dc20cb15f692dfd))

* #61, #62, #63, #69
Some more work towards version 2.
Using more views and selects in commands
Removing redundant code
Updating some of the tasks and re-enabling them slowly ([`3ad6f6e`](https://github.com/ESloman/bsebot/commit/3ad6f6edd6ec65a39c328d8ffb8f75758081a7eb))

* #61 #62 #63 #67
Lots of work and changes to begin upgrade to Version 2. This includes the beginnings of using pycord over discord.py, thread usage, better ways to create, close, and place bets using Views and Modals. ([`b3c8e70`](https://github.com/ESloman/bsebot/commit/b3c8e70c8711a903289164809b3ab4579464c1d2))

* Fix issue with victories ([`541b7ce`](https://github.com/ESloman/bsebot/commit/541b7cece0a12d769926f3335f373eb25d837ef8))

* Fix the wordle value ([`9bcdb58`](https://github.com/ESloman/bsebot/commit/9bcdb588faa25432a7c71c82ef5282fb15afba51))

* bug fixes ([`6a38fc5`](https://github.com/ESloman/bsebot/commit/6a38fc518a9085ffa89a0980709e0d84059e38cb))

* Add wordle support and disable eddie rot ([`6bd0ea9`](https://github.com/ESloman/bsebot/commit/6bd0ea91e248d11fb3c50fb391672afe71258e8e))

* Add project zomboid options
fix auto generated bets ([`e449ee9`](https://github.com/ESloman/bsebot/commit/e449ee970461e4ac8acff61966ec82a090f91695))

* Make the kill time about 5 minutes ([`cfd828d`](https://github.com/ESloman/bsebot/commit/cfd828d850a37e2fdb9f84affe14e82ab39d003f))

* Fix error ([`9194283`](https://github.com/ESloman/bsebot/commit/91942835e9d012ed7d35e6bacc70b932ed811361))

* Limit who can solo in the server ([`a234ad6`](https://github.com/ESloman/bsebot/commit/a234ad6eaf0ef5da8add0e9db60eac32ff4d6750))

* Add toggling the updater.service ([`b56dd91`](https://github.com/ESloman/bsebot/commit/b56dd91a18688d8e52e7cda1160d89df5b77c32d))

* Add support for MC 1.18 ([`0bf1ae5`](https://github.com/ESloman/bsebot/commit/0bf1ae5508319e1c461a7dd7aa3875df98a475ef))

* Add timeout_str option to autogenerated bets ([`1395d7e`](https://github.com/ESloman/bsebot/commit/1395d7ed28d9bd360a928c8be3a13ff17dae3595))

* Adding in autogenerated bet for pook rants ([`ded09d3`](https://github.com/ESloman/bsebot/commit/ded09d38f2aaff8c700892c4a21f1ff80cd2e59d))

* Add new breakdown of salary information for the users. Available in the `/bseddies predict` command and in daily salary messages. ([`c0ea943`](https://github.com/ESloman/bsebot/commit/c0ea9430c0b88e90be253ad15e484859f5ef37d0))

* Testing new breakdown in the salary messages ([`a840223`](https://github.com/ESloman/bsebot/commit/a840223cfa1c31ed87186a5c151493462b4d3531))

* Fix bug with high score list not expanding properly ([`86873aa`](https://github.com/ESloman/bsebot/commit/86873aafed946925ac8207a284934cad9a192a54))

* Fix issue with PartialEmoji types not registering properly ([`c9cea77`](https://github.com/ESloman/bsebot/commit/c9cea77f95a29ddc5a551b3cac54a184bdb72c5a))

* Adding eddie rewards for getting replies to your messages. Also allow messages to have multiple types. ([`b882cee`](https://github.com/ESloman/bsebot/commit/b882cee5f32766f4325c47c6cb7ca1e58c3dbc78))

* Actually had one to the days so we&#39;re predicting correctly ([`c60baaa`](https://github.com/ESloman/bsebot/commit/c60baaa10d8af1d96de1f63a3232476c95db39f2))

* Tidy up the message a bit and add some documentation ([`70adcbe`](https://github.com/ESloman/bsebot/commit/70adcbe5d16e9ca71dc637169df80b4019558d7f))

* Attempting to add &#34;predict&#34; method ([`2d4771e`](https://github.com/ESloman/bsebot/commit/2d4771e376c937446bf188d25fe0c1baee238d4b))

* Fix custom emoji reactions not being registered ([`bde8c1d`](https://github.com/ESloman/bsebot/commit/bde8c1d85511e6d5a569f5dbd30b607f5d6731b4))

* Lock in the eddie amount of KINGs when the event fires. This prevents users from giving away their eddies before they get cut in half. ([`a5b5615`](https://github.com/ESloman/bsebot/commit/a5b56152886f57320e0e65ad81a377458a20b317))

* Remove the on_interaction event as it&#39;s a future feature and not public yet ([`611bb2f`](https://github.com/ESloman/bsebot/commit/611bb2f95ce70c982b34e820f610d7f6e9040a95))

* Added eddie bonuses for &#34;reaction_received&#34; events and added all the logic for handling reactions to messages
Also updated the daily minimum ([`f48c222`](https://github.com/ESloman/bsebot/commit/f48c22278a590080685125b0c2b7ce4512993b77))

* Update some of the message values ([`512ba77`](https://github.com/ESloman/bsebot/commit/512ba77213fc0e765eb20a5f9b713c780ef0c8e5))

* Lots of minor updates to hopefully improve things ([`21b8551`](https://github.com/ESloman/bsebot/commit/21b855111978398c7c29adb61090ecf99acaea26))

* Fix bets not appearing due to weird deferral logic ([`3723235`](https://github.com/ESloman/bsebot/commit/3723235ecf3aecd488e3e87ad1d5d0212fbb56fb))

* Add support for members leaving the server ([`7600dda`](https://github.com/ESloman/bsebot/commit/7600ddac979f1cfa490a65b20c61385451c0056f))

* Multiple QoL updates:
- stop more &#34;interaction failed&#34; messages by using ctx.send instead of ctx.channel.send
- prevent &#34;inactive&#34; users from being king or getting daily eddies
- when a user joins - if they exist already - just set them to &#39;active&#39; again ([`673bc75`](https://github.com/ESloman/bsebot/commit/673bc75ded6268fb91aa8aa253f874bc063ad872))

* Add support for new version of discord-slash library ([`8fa45d7`](https://github.com/ESloman/bsebot/commit/8fa45d7dff3896baf6a5cd3527cbc421354302ab))

* Re-enable Valheim reporting and allow the boys to use the commands again ([`267ac79`](https://github.com/ESloman/bsebot/commit/267ac799897f9c02e4e9554814c12952a715e486))

* Disable valheim reporting ([`a0e6137`](https://github.com/ESloman/bsebot/commit/a0e6137d6588e40be814b5dddd6e84d5872253ea))

* disable these commands ([`64b5653`](https://github.com/ESloman/bsebot/commit/64b56537d3bbd5789358b62db070b257bf4e5bd3))

* Change server info polling to be once every 12 hours whilst it&#39;s off ([`afc85dc`](https://github.com/ESloman/bsebot/commit/afc85dccffdec19759696c30b286924b01cffb33))

* Allow &#39;server admins&#39; to turn the server on/off and start/stop the different game services
Add some more private channels to constants ([`20def4e`](https://github.com/ESloman/bsebot/commit/20def4eb06265d588adebef7cd5e4ab519f96557))

* Update player disconnect logic ([`672b39b`](https://github.com/ESloman/bsebot/commit/672b39b5c2f5a284a4cc84f763ba9245316e2fd6))

* Add basic framework for #60
- allow users to turn specified game servers on
- wait 5 minutes after all players disconnect before shutting down the server
- add some more exception handling
- remove redundant logging ([`0bcc9e1`](https://github.com/ESloman/bsebot/commit/0bcc9e1038ba529ce7d54a6a72c35b9726b67838))

* Add better handling for exceptions here ([`0323aae`](https://github.com/ESloman/bsebot/commit/0323aae5250ff531529f208936f4e2e3eb45eebf))

* Catch unknown exceptions ([`b92dc8e`](https://github.com/ESloman/bsebot/commit/b92dc8ecc3d8066208028dae0d26f42ba2fb484b))

* Actually fix the player iteration ([`fc0e174`](https://github.com/ESloman/bsebot/commit/fc0e1741cb505216e4642e203817431367649b02))

* Fix issue with minecraft player reporting ([`a5ec782`](https://github.com/ESloman/bsebot/commit/a5ec7827f04404b07924b37506958a315aaf9ee8))

* Add extra formatting here ([`c2849c9`](https://github.com/ESloman/bsebot/commit/c2849c9ac7b91461e819568cda7762c44076c2d1))

* Remove async query cos it&#39;s not implemented yet ([`750339f`](https://github.com/ESloman/bsebot/commit/750339fd59a2a9e0982b8416d69104e32f1bad80))

* Add logic for handling minecraft servers ([`49ca6d4`](https://github.com/ESloman/bsebot/commit/49ca6d425ca026308cf576d133f2705c67e84845))

* Add functionality to stop server restarting in &#34;debug&#34; ([`93e3188`](https://github.com/ESloman/bsebot/commit/93e3188302d14d625a333aaa8ddfc68994759087))

* Remove logging from this task ([`bed7f18`](https://github.com/ESloman/bsebot/commit/bed7f184a37bd6b2c094805f5ae83e75f3546a74))

* Adding in some try/except handling for failed ssh connections and removing debug try/except ([`2717d88`](https://github.com/ESloman/bsebot/commit/2717d88fc4fdff8cfa234cfd024ec0eb96e91c0e))

* Add another exception for steam rcon call ([`2b5b1f0`](https://github.com/ESloman/bsebot/commit/2b5b1f0bbabffe31e704315ea74841b6888a31ad))

* wrap the whole thing in an exception block ([`f0a0774`](https://github.com/ESloman/bsebot/commit/f0a0774ea4d6943601e5c41826c38dd7c4432f91))

* Change interval times ([`fea4efb`](https://github.com/ESloman/bsebot/commit/fea4efbd14062473a7b160dbd02f8bfa252b9fac))

* Removing debug after fix and adding task restart in command off ([`7c299f6`](https://github.com/ESloman/bsebot/commit/7c299f6828d9e7bfb0421e46f96a193243370acd))

* some debug? ([`be62ca8`](https://github.com/ESloman/bsebot/commit/be62ca8a6455d10c0246a96aca383c75632c047d))

* Attempt at making sure the task starts immediately ([`e7452a2`](https://github.com/ESloman/bsebot/commit/e7452a2c94580965c4c9edae427653e26b200a41))

* Don&#39;t change interval when stopping the instance ([`08190ef`](https://github.com/ESloman/bsebot/commit/08190effebf6e6b44d1330723c17ae805f6fd24d))

* Logic for controlling the AWS Game Instance
This effectively resolves #56, #57, #58 and #59.
- Add commands to turn aws instance on and off
- Add task to update a &#34;status&#34; message with server info and connected players
- Add task to turn off the server if uptime is above a certain amonut and no-one is connected ([`752e50e`](https://github.com/ESloman/bsebot/commit/752e50e9529a97ffdb235fad0dbc4999f8231477))

* Prevent users from betting negative eddies, resolves #54 ([`62f1a1a`](https://github.com/ESloman/bsebot/commit/62f1a1a68eb5bf971567608e9a17f7fd9884d6f6))

* Change interval to 5 minutes ([`4b536e1`](https://github.com/ESloman/bsebot/commit/4b536e1e2bd1e227614bd3f7757677da3a3fe238))

* Add some logging for changing time intervals ([`e64a659`](https://github.com/ESloman/bsebot/commit/e64a6591b6a81375275bb0fb0ac81a6a6bab2332))

* Change the number of autogenerated bets created

Use a randomly generated number of random bets ([`4ee0ac3`](https://github.com/ESloman/bsebot/commit/4ee0ac37d81970e775ccb172bd86f517ba032d1f))

* Change daily minimum to 3 eddies ([`5e7be32`](https://github.com/ESloman/bsebot/commit/5e7be32c493997aabd57652adb2bd2017431eb64))

* await/async stuff ([`018e832`](https://github.com/ESloman/bsebot/commit/018e8329e22bdee5d20c045b37d79a8a42354e5e))

* Better implementation for #52? ([`f2e1293`](https://github.com/ESloman/bsebot/commit/f2e1293a86b3ecb15fe9e7d2883841a0db936466))

* Make the make &#34;chance&#34; for a revolution event 75% ([`d9ecfc2`](https://github.com/ESloman/bsebot/commit/d9ecfc2235bc91d7f81c770b31a6e63be0bdd888))

* Make BSEddiesKingTask have it&#39;s own name to avoid conflicts ([`7a6c6b6`](https://github.com/ESloman/bsebot/commit/7a6c6b689bcf63fae2afa9693fe7ae0e5e8f25e1))

* Fix erroring out due to user leaving the server ([`d5e1868`](https://github.com/ESloman/bsebot/commit/d5e18688de3d5e151e1ecf26ec682e7a8be96d91))

* Fix erroring out in leaderboard when someone is no longer in the server ([`3f75fb6`](https://github.com/ESloman/bsebot/commit/3f75fb6a4727d5afa4ecd78cb86de9223590a8fe))

* Add support for #53 - logging each SlashCommand for every user, resolves #53 ([`2f6c38e`](https://github.com/ESloman/bsebot/commit/2f6c38e619e02c74f1c7f606ea956320eed6fc4a))

* Make sure we don&#39;t send false alarms if the last cull was more recent than the time limit ([`4ea2def`](https://github.com/ESloman/bsebot/commit/4ea2def25beb62a5cc28910d4244a1ead1957cb0))

* Resolves #52
Add in warnings to allow users to know they&#39;re about to be culled
We send one warning to the user about 24 hours before they get culled. ([`b9cb43d`](https://github.com/ESloman/bsebot/commit/b9cb43dd3a1486725cc8308ad3713f5452b4a724))

* Add &#39;@everyone&#39; tag to the revolution event ([`aa5bc0a`](https://github.com/ESloman/bsebot/commit/aa5bc0afdfd9b2970d6344169cd50e47798c7d03))

* Finish off the work for #40
- added a method to send a random gif in the &#34;countdown&#34; phase
- change loop timer to be more frequent as we get closer to the expiry of the event
- change loop timer to be minutes on the day of
- change loop timer to be 8 hours when it&#39;s not a sunday (ie it&#39;s never going to go off)
Resolves #40 ([`82d6869`](https://github.com/ESloman/bsebot/commit/82d6869f7754ce1ab7399596972c8d7da1395834))

* Add in logic that gives users with &#34;pending eddies&#34; a bit longer before they&#39;re culled ([`452e73f`](https://github.com/ESloman/bsebot/commit/452e73fb065d7b5c45599d632a25febfe1015683))

* Make the revolution event GIF random ([`17e047d`](https://github.com/ESloman/bsebot/commit/17e047dc2cffec8beeeec8a083911e1826d7ab15))

* Some minor tweaks
- Make sure that users also gain at least one point from a user&#39;s inactivity
- Use the right list when determining grammar correctly
- re-ordering logic when determining who gets points for user inactivity ([`30f9772`](https://github.com/ESloman/bsebot/commit/30f97727e56ae066bc54992ebc24bdacdf346da1))

* Fixes a couple of bugs:
- Fixes #50, make sure KING loses eddies
- Fixes #51, make sure we use USER_CREATE interactions so we know how long to wait before we try and cull new users ([`d5c9319`](https://github.com/ESloman/bsebot/commit/d5c931975922fc2fdb7cfe7a5c62215308967ce6))

* Update inactive user task with another interaction to ignore ([`7f9d90a`](https://github.com/ESloman/bsebot/commit/7f9d90a57fecf418b9c41375e6c75188d8bdb8f6))

* Update revolutiontask.py

Fix typo preventing code execution ([`0a27199`](https://github.com/ESloman/bsebot/commit/0a2719927e89bdcf8b15d7f02daf6a2d68f2c56a))

* Add some debug logging to the revolution event #40 ([`2e2ea9e`](https://github.com/ESloman/bsebot/commit/2e2ea9e350e8de7212a401a46527f7de4f7211df))

* Updates to inactive user task
- make the culling period shorter to account for weekly revolution events
- restrict the events that count as &#39;interactions&#39; ([`bdfce25`](https://github.com/ESloman/bsebot/commit/bdfce255da02f81948891a135adb77323c0115d8))

* Make revolution event have a 3.5 hour expiry time - #40 ([`75d8da1`](https://github.com/ESloman/bsebot/commit/75d8da1a3d36196af01fcbecd27c17d7a3f718ba))

* Add basic framework for messaging people a random gif if they say &#34;thanks&#34;
- added aiohttp api class for giphy, resolves #41
- added random gif method for said class
- use said method in a DM handling class, resolves #10 ([`32ef6e5`](https://github.com/ESloman/bsebot/commit/32ef6e5075685f7e8b2614588396580cbd9c890b))

* Final bit of functionality for revolution events #40:
- Add file to create event in DB
- Add actual channel ID
- Allow passing in of channel ID to DB entry creation logic
- Chance success calculation more accurate ([`6bd2755`](https://github.com/ESloman/bsebot/commit/6bd275570946c4025e3423ef9bc94a564bbd035c))

* Remove the admin requirement from the &#34;/bseddies king&#34; command #43 ([`c8db2df`](https://github.com/ESloman/bsebot/commit/c8db2dfd9bd3e1dfc082366d893c05c5b88d3903))

* Use the ACUTAL KING&#39;s uid, #43 ([`c5b0b36`](https://github.com/ESloman/bsebot/commit/c5b0b36682b19c1736e28dbab51a7e76069d3cb3))

* Make the KING message available for all, tag the actual KING and put the &#34;total&#34; time into days/hours/etc.
Resolves #43 ([`6fa8776`](https://github.com/ESloman/bsebot/commit/6fa8776d2d3e6ea3b355bc063e94256638a8a434))

* Couple of extra slash commands:
- &#34;/bseddies admin switch&#34; - resolves #44
- &#34;/bseddies king&#34; - first bit of work for #43 ([`6efdedc`](https://github.com/ESloman/bsebot/commit/6efdedc96f65f0f4513434b5a17f963f73dbf6a6))

* Fix activity type being set incorrectly for KING_GAIN ([`91bdf3f`](https://github.com/ESloman/bsebot/commit/91bdf3f3fa421f9a195740c8618cac9255a6450c))

* Change a math.floor to math.ceil so that users get 1 point minimum ([`0702e5c`](https://github.com/ESloman/bsebot/commit/0702e5c30118d1833ae95fba353e539b62b10229))

* Change the inactive user task to take into account new transactions possible ([`a203333`](https://github.com/ESloman/bsebot/commit/a2033331ad8d37e65f2bd737655581508dd6a939))

* Change inactive point cull to 75% of user&#39;s current points ([`3b7233f`](https://github.com/ESloman/bsebot/commit/3b7233fdcca516c7a5ff8c77664fc7bdf91211da))

* Change the text so we don&#39;t repeat &#34;here are all the X bets&#34; again. Extra commit for #48 ([`4c3edcd`](https://github.com/ESloman/bsebot/commit/4c3edcd845bea0da2f7e939cd22592051d479b8f))

* Fix pending and active bets working with lots of pending/active bets by sending multiple messages ([`139ccc2`](https://github.com/ESloman/bsebot/commit/139ccc22d637de88d8e2611db22f4fb540fc0184))

* Make sure that any slash commands that don&#39;t send ephemeral messages do send an acknowledgment ack to make sure we don&#39;t get this bloody error message - resolves #47 ([`5f12265`](https://github.com/ESloman/bsebot/commit/5f12265f78f00eadaa1d1496b3fd96593ceded26))

* Put highscores back in the pool ([`e5e56cd`](https://github.com/ESloman/bsebot/commit/e5e56cda95637dbfcf4d65e0bd68bf9c944814df))

* Revert &#34;Change leaderboard to just &#39;leaderboard&#39; in an attempt to fix the issue #47&#34;

This reverts commit ad7725f84dac0eacf6ac42c0c5fb0a178ef846ce. ([`9fc138a`](https://github.com/ESloman/bsebot/commit/9fc138af21e3d0af8394549bb2ce38d6e557021b))

* Change leaderboard to just &#39;leaderboard&#39; in an attempt to fix the issue #47 ([`ad7725f`](https://github.com/ESloman/bsebot/commit/ad7725f84dac0eacf6ac42c0c5fb0a178ef846ce))

* Register commands again - attempt to fix #47 ([`4e0597d`](https://github.com/ESloman/bsebot/commit/4e0597d3accecb15f4faead8b4c667cca46fb829))

* Attempt to fix the &#34;interaction failed&#34; issues #47 ([`5d103f5`](https://github.com/ESloman/bsebot/commit/5d103f5c731934755a507e48cfa09cca94cd575e))

* Change the daily salary to round down rather than round up ([`36b83b8`](https://github.com/ESloman/bsebot/commit/36b83b86279cb6a49460900686e1ff02279d70f9))

* Various changes:
- fix the grammatical mistakes in decay messages, resolves #46
- changed the number of personalised bets in autogen to 1
- Added a &#39;high score&#39; leaderboard for displaying high scores only, resolves #42 ([`03e646b`](https://github.com/ESloman/bsebot/commit/03e646b97ca3ccf0d5dbf0adea44d882e7279ffb))

* Actually add the functionality and deducts and adds points for each user - #40 ([`f2c5490`](https://github.com/ESloman/bsebot/commit/f2c549027cd29f283387b738350b25e8ee897685))

* Use message channel ID and not guild ID for #40 ([`e1f288c`](https://github.com/ESloman/bsebot/commit/e1f288cf13fa1eee39998ae4c4e904805aa8d602))

* Change the default channel ID for #40 whilst under test ([`a71bed2`](https://github.com/ESloman/bsebot/commit/a71bed2a61a3efac8656ff2a8941f2c2efc5fdb1))

* Beginnings of #40. This adds:
- mongo classes for interacting with revolutions
- task for creating/resolving revolutions
- add reaction event class for revolutions ([`d3e9dd8`](https://github.com/ESloman/bsebot/commit/d3e9dd87b1ddcfa9a7481234d0f94ff33f5062ab))

* Some minor fixes:
- fix a bug if we didn&#39;t have high_score in the DB for a user
- add limit to the number of non-generic bets we can get autogenerated ([`ddae3ab`](https://github.com/ESloman/bsebot/commit/ddae3ab0511f4a4dd9ac6e5a6e9b1c6e6fa94793))

* Completes the first three tasks for #42.
- Added functionality to maintain the high score
- Added high score into `view` command ([`5d6b4c0`](https://github.com/ESloman/bsebot/commit/5d6b4c0ed453c202be1d25640737112e8847d75f))

* We don&#39;t particularly care or need to do anything if the user doesn&#39;t need any points culling ([`c540ab9`](https://github.com/ESloman/bsebot/commit/c540ab966f077f96dfe297564af62df3b62ea667))

* Update #39 to actually take the points away from the users and re-distribute them to the other active users ([`78a8d11`](https://github.com/ESloman/bsebot/commit/78a8d11230c1d57f5bd4ae74314445a5f68d67a0))

* Further updates for #39
Moved some of the logic into a separate method to avoid duplication ([`0ffab3e`](https://github.com/ESloman/bsebot/commit/0ffab3e2b73b0350236f8c8d922ba755a5962c40))

* More updates for #39
Added the logic for sending the user&#39;s a notification to say they&#39;ve gained eddies ([`3a699ce`](https://github.com/ESloman/bsebot/commit/3a699cebd5a073e81847d474612db814a161f762))

* Tidy up debug logging and add some enum values for #39 ([`2496e9a`](https://github.com/ESloman/bsebot/commit/2496e9a4ecbccabe5cd714141f3a79f26088c389))

* Further updates to #39 - counting points and testing how much everyone will get ([`9ddd340`](https://github.com/ESloman/bsebot/commit/9ddd34047b762a615d4f7c2f9aa00c67bc71e157))

* Further updates to #39 - add function to work out how many points must be taken ([`d21d7e6`](https://github.com/ESloman/bsebot/commit/d21d7e6b20f46b5fc1b6b3a168ab07fbe14ff838))

* Update for #39 to actually account for recent culling properly ([`13ec331`](https://github.com/ESloman/bsebot/commit/13ec3316d1c2320a1193783f18ba132bc959c351))

* More updates for #39 - testing functionality to log cull ([`bf35126`](https://github.com/ESloman/bsebot/commit/bf35126d530fc8d691a9b1b57135b79528d421d3))

* Add basic framework for #39. This doesn&#39;t do anything yet except check the users and log who&#39;s done what recently ([`e3e948c`](https://github.com/ESloman/bsebot/commit/e3e948cfded0556ff724275c5c7c0fe861eda5cc))

* Make sure the admin command can only be used by me ([`18dd797`](https://github.com/ESloman/bsebot/commit/18dd79721eabf747c517463ef0c20fde3f894d35))

* Adding &#34;/bseddies admin give&#34; command for admins. This allows an admin to give a user X amount of eddies if they so wish. Resolves #33 ([`8afd25a`](https://github.com/ESloman/bsebot/commit/8afd25ac46dbf5d0bd3f5f7d669d59dd8484072e))

* Up the number of active bets I can make ([`bcb11bb`](https://github.com/ESloman/bsebot/commit/bcb11bb6d31bfa0f4141cfbe553ed6477550497d))

* Fix a bug where we weren&#39;t stopping at 3 autogenerated bets ([`12cc43a`](https://github.com/ESloman/bsebot/commit/12cc43a8d9730299f95467b7c81ce6e4bb3a1c05))

* Add functionality to check voice channels for online members if the bet specifies it needs some people, resolves #37 ([`c4e7b91`](https://github.com/ESloman/bsebot/commit/c4e7b91a271137601fecdabc226b22620a39e376))

* Added framework for Auto Generated Bets:
- created Collection class for inserting bets to select from and selecting bets from the DB
- Add slash command to trigger bet generation
- Add json file to parse with the bets in ([`c518e19`](https://github.com/ESloman/bsebot/commit/c518e197428a369a0e2e291f12f5d5225ab6f84c))

* Some minor refactoring:
- created a &#39;reactioneventclasses&#39; file for classes for each reaction event type we&#39;re handling
- move the logic for reaction client events to the above file
- moved the BaseEvent class to a separate file
- tidy up some of the imports in a few files ([`8d40963`](https://github.com/ESloman/bsebot/commit/8d4096381333c313f9a5643ec322248649a5d153))

* Update betmanager.py

Fix bug that causes bets not to close properly ([`c65a5f1`](https://github.com/ESloman/bsebot/commit/c65a5f1d417433554a867f0ddd173ce7eb696e32))

* - Add collection class for loans
- Added slash commands to take a loan, repay a loan, and view your loan
- Added tasks that consistently checks that loans haven&#39;t expired
- Added additional framework that makes these loans possible: transaction types, constants, etc

All this resolves #20 ([`24d306d`](https://github.com/ESloman/bsebot/commit/24d306d2d3bd8a09a605c082612895db5092935b))

* Make sure we append user ID to recent transaction history items too for #9 ([`5f76172`](https://github.com/ESloman/bsebot/commit/5f761728b15cd2165b7424e00592ce4ab572c8cb))

* This completes most of the work for #9
- Allow user to specify if they want the full transaction history
- Create a XLSX file with the user&#39;s full history and send it to them if they so wish ([`ed51117`](https://github.com/ESloman/bsebot/commit/ed51117a78f486e14216ef9b3a747f8e7797e81e))

* Resolves #32
Changed the algorithm to be fairer. We&#39;ll monitor it and see how it feels in the long run. ([`a1b7510`](https://github.com/ESloman/bsebot/commit/a1b7510729bc972ff58e00cc2c6ed132ace78002))

* Fixed a bug that prevented daily salary messages going out ([`75eafe6`](https://github.com/ESloman/bsebot/commit/75eafe662f1266fdc79ed45a99bcb292638dd6c2))

* Add setting user flags in the DB for the current KING, closes #14
Give the KING an extra couple of active bets, closes #15 ([`28e63f5`](https://github.com/ESloman/bsebot/commit/28e63f54b8421c40d540d2a5a12519c62a971ff1))

* Added the amount of eddies you lost in the &#34;losing bet DM&#34;, resolves #31
Added the name of the result too in both winning and losing DMs ([`5563649`](https://github.com/ESloman/bsebot/commit/55636491795b1630130fdf9baa09f55ad421e738))

* Resolves #30
Move the checking point total logic to before the point we add someone to a bet if they&#39;re betting for the first time ([`fba515f`](https://github.com/ESloman/bsebot/commit/fba515f09f78dc3ab9b65d7cdc280775b7c3dec9))

* Resolves #13
Added a message to the old KING and the new KING informing them of their change of status ([`d798fa8`](https://github.com/ESloman/bsebot/commit/d798fa80682fb26a706a582b1b6e9249f5990654))

* Resolves #17
Add the framework and functionality to allow users to toggle the daily notification about their daily allowance. ([`44d2947`](https://github.com/ESloman/bsebot/commit/44d29473813fa65c2669ab154dda7ce24f5f75b4))

* In the daily summary message - include user display name too and not just the ID ([`f09f03e`](https://github.com/ESloman/bsebot/commit/f09f03e992a52514153f04f88ec864d714bf1839))

* Add transaction history command, completes a task for #9 ([`1f87d20`](https://github.com/ESloman/bsebot/commit/1f87d20e530183f6e53271c028592a9bbee4fe75))

* Summary of changes:
- change the way we distribute eddies on a win, resolves #28
- prevent users from winning their own bets if they are the only better, resolves #27 ([`2e5257f`](https://github.com/ESloman/bsebot/commit/2e5257fbaa0fc337c43be8e5d0eb4da8952d149b))

* Resolves #25
We put the &#39;title&#39; as part of the description now and make it bold. Have to use some regex to get the bet ID out of this now. ([`36c5856`](https://github.com/ESloman/bsebot/commit/36c5856279395a0289fc216b6d98338d4fda112c))

* Resolves #11
Use &lt;&gt; tags on URLS to stop embeds being generated ([`5ecaf8e`](https://github.com/ESloman/bsebot/commit/5ecaf8e5cff3d6c8a8a6e92d7c6b34edca80b083))

* Some minor fixes and improvements
- Log DM&#39;s to the bot properly so we can analise the contents
- Add another private channel to constants.py
- Make sure the creator gets extra bets ([`c802b9d`](https://github.com/ESloman/bsebot/commit/c802b9d79d665a393c82a90e269a6f7632751d81))

* Resolves #26
Add code to update king history on change ([`94f4593`](https://github.com/ESloman/bsebot/commit/94f459373004a7b75f2d0d2564159be0e2cdc76e))

* Adds to #26.
Need to actually commit the part that does that change ([`6ce1adf`](https://github.com/ESloman/bsebot/commit/6ce1adf594b573fd8d66c5dcf3be77bb93281c0a))

* Adds to #26. Collection class methods for keeping track of this stat. ([`208e1e8`](https://github.com/ESloman/bsebot/commit/208e1e888049ddd746cca9f3ea5b67719eb970a7))

* Resolves #24
Set default timeout to ten minutes rather than five
Add another class instance check to validation
Re-organise imports in main.py ([`91ea0e3`](https://github.com/ESloman/bsebot/commit/91ea0e3d956ce63a9c4b0aa8c3e73ceafc22a6fe))

* Added more comments for type hints for #16
Resolves #21 by increasing the number of outcome names by 2 ([`d473af1`](https://github.com/ESloman/bsebot/commit/d473af1651e51eae691a47e6cd4ef2e8ce434f58))

* Add an OVERRIDE type to TransactionTypes enum ([`57ff02d`](https://github.com/ESloman/bsebot/commit/57ff02d717d91fc5df403e05f58f636cb932a1b6))

* Update README.md

Added a much more details README file. ([`505bd35`](https://github.com/ESloman/bsebot/commit/505bd35f694c777cc89a2da62b195a37a3fb9106))

* Making sure we import typing.Union ([`a61fd33`](https://github.com/ESloman/bsebot/commit/a61fd339a26e5a7ca13c8f2c182605e209da13ba))

* Add a bunch of comments and type hints to a couple more files to #16 ([`15520b9`](https://github.com/ESloman/bsebot/commit/15520b9b943fcb7b160f0b7ea2cc28ccc2af3111))

* Some more minor fixes:
- add in &#34;DEBUG_MODE&#34; flag and set our guilds based on that and not BETA_MODE
- Get booleans for BETA_MODE and DEBUG_MODE correctly
- added some comments to main.py for #16 ([`778ddfa`](https://github.com/ESloman/bsebot/commit/778ddfa27d9e16673e5665953a464063a892caff))

* Some minor fixes:
- Make sure that the transaction history entries that take away points are indeed negative
- Make sure we have the &#39;daily_minimum&#39; key when we&#39;re processing daily eddies ([`e99c0fa`](https://github.com/ESloman/bsebot/commit/e99c0fa777f1fbf34e39764d3a128e42f5f6cd6b))

* More updates for #16.
Updated this files with more comments and type hints ([`11c9f4e`](https://github.com/ESloman/bsebot/commit/11c9f4ed4c2bba1831bcd67b7501b2c13699050b))

* More updates for #16
Updated this file to have type hints and better comments ([`53a472f`](https://github.com/ESloman/bsebot/commit/53a472f9eb674ead991ab928bfaf6044022b86a1))

* Beginnings of #16.
Update this file to have type hints and some better comments ([`bd7176e`](https://github.com/ESloman/bsebot/commit/bd7176e7854a2607c5912cfcb7a843e96c22eb9c))

* Resolves #4
Mostly resolves - add in the framework and functionality for keeping the transaction history of eddies for each user ([`c9052af`](https://github.com/ESloman/bsebot/commit/c9052afbde34334fc2ab20d7a746909a16db3430))

* Added a try/except statement and removing some redundant logging ([`f210f1b`](https://github.com/ESloman/bsebot/commit/f210f1b62b93e8a4b3da0f1a52fddc4fc7380f31))

* Closes #5
Added logic for users not interacting with the server. ([`6a03501`](https://github.com/ESloman/bsebot/commit/6a03501b8342a9cf0667f1bbbf7f9685c69592d2))

* Update UserPoints collection class to have methods for getting/setting the daily_minimum ([`5d31cd6`](https://github.com/ESloman/bsebot/commit/5d31cd62eb812801174674775a6ae6def7f8f787))

* Add correct comment to method ([`2695e20`](https://github.com/ESloman/bsebot/commit/2695e20d0abc99bcbc9d9913cd568b42746e4d55))

* Make this task 2 minutes and not 10. The basic operation - which doesn&#39;t need any network operations - is quite rapid so we&#39;re less worried about it taking resources ([`62a1231`](https://github.com/ESloman/bsebot/commit/62a1231e5c948fa036d374f3c00d0fdde4715b18))

* Closes #8
Add in a task that continuously checks who&#39;s the KING and assigns/unassigns the role as needed ([`c83238f`](https://github.com/ESloman/bsebot/commit/c83238f83dbd7e1039598744a16386c529fa0459))

* Update slashcommandeventclasses.py ([`3f54e2f`](https://github.com/ESloman/bsebot/commit/3f54e2f2d446efe53e4f2a1925b51af5d5ebcee3))

* Update slashcommandeventclasses.py

Fix bug where we weren&#39;t using the correct variable ([`8e68292`](https://github.com/ESloman/bsebot/commit/8e682920ac62be5e67ad406f367c66b401b09a17))

* Add logging display name + eddie gain
Remove redundant log message ([`81ab8ba`](https://github.com/ESloman/bsebot/commit/81ab8bab0275731741ee8670863227fca77fbebd))

* Add static list of PRIVATE_CHANNEL IDS and set private property on bet if the channel id is within that list ([`68a44f6`](https://github.com/ESloman/bsebot/commit/68a44f6e9b08257dc5cbe8bd7277b78b34413fc1))

* Don&#39;t restrict bets to non-private ones as this is a hidden message ([`e493d07`](https://github.com/ESloman/bsebot/commit/e493d07ac5c69560920409844962b2e8e683f682))

* Closes #3
Actually fixes it this time. Move get_user_pending_points to UserBets class rather than UserPoints class ([`60e8d2e`](https://github.com/ESloman/bsebot/commit/60e8d2ee791333e5086a83eb977c99c56c2d5551))

* Resolves #3
Change the way we handle pending points. No longer bother tracking the stat but query for all pending bets for the user and add up all the bets. This is a much more accurate way of doing it. ([`e9ffa2d`](https://github.com/ESloman/bsebot/commit/e9ffa2d30573b81c242741e5e697d0c4253c5a6a))

* Add &#39;/bseddies pending&#39; command. This returns all pending bets the user has invested bseddies in to ([`19b1e53`](https://github.com/ESloman/bsebot/commit/19b1e5300325069fcc767bc1498d8a3cdd0b6ede))

* Make the &#39;active&#39; command return all the non-closed bets and state which ones can be bet on or not. ([`9ead453`](https://github.com/ESloman/bsebot/commit/9ead453d406882fc75764f38f8858c8c0bbbb745))

* Fix erroring out when we can&#39;t send a message to a user. This also prevented us deleting the json file and possibly sending messages twice. ([`a61c39a`](https://github.com/ESloman/bsebot/commit/a61c39a43220c80d446bacc597219b02ba15520e))

* Make sure all users with &#39;The Boys&#39; role get a DM with their daily salary of eddies ([`b396c70`](https://github.com/ESloman/bsebot/commit/b396c70d241497eb341c0672b45d964ea3e9a2a1))

* set_points method was using wrong DB key ([`e0cb338`](https://github.com/ESloman/bsebot/commit/e0cb338a32e5ef721505d0fecfd370b01f25b756))

* This is an attempt to resolve an issue where a user can spam the reaction to trigger multiple reaction events and maybe get an extra BSEddie out of it. At the end of a transaction, we simply make sure that we still have non-negative BSEddies. If we do, then we revert what we did and return.
Fixes #1 ([`61c73de`](https://github.com/ESloman/bsebot/commit/61c73de7103a69c78176d2e9d05bf19d035493c4))

* Fixes #2
Add outcome name to &#34;bet closed&#34; message ([`4a3c33f`](https://github.com/ESloman/bsebot/commit/4a3c33f3fee1f068b8b6967311959e96f54b2d00))

* Commit changes to take us out of BETA ([`418c43f`](https://github.com/ESloman/bsebot/commit/418c43ffc8cfea8988a31d1c939e8f23fa96283d))

* Add correct key for setting pending points
Make sure we&#39;re decrementing pending points correctly
Add method for getting pending points
Add pending points total to &#39;view&#39; points command ([`562824d`](https://github.com/ESloman/bsebot/commit/562824d43a96836a4d8f623dbcf5d8ae46fc9731))

* Fix some minor bugs in previous commit
Add functionality to disallow users from creating too many active bets ([`7a8e8bc`](https://github.com/ESloman/bsebot/commit/7a8e8bcf6f9e2ffa5e5500e0a984e1f24e62e429))

* Big pre-release update.
- Make sure that bets exist before we attempt to place BSEddies on them or close them
- Make sure that users actually get their daily salary gain
- Make sure that we apply daily salary gain to all server members and not just those that interacted with the server in the last 24h
- Add loggers rather than print statements and actually output to a log file
- Add &#34;pending_points&#34; entry and attempt to track that
- Make sure we add a new user to the DB when a new member joins the server
- Only make sure we message the boys about their daily salary gain
- Moved the final stuff over from command manager classes to the right event classes
- Added lots more method comments to make it easier to understand what the methods are doing
- Removed some redundant code and imports ([`ebc1dff`](https://github.com/ESloman/bsebot/commit/ebc1dff58a52efe86b838aba407d7eb46f1bac39))

* Remove &#34;debug&#34; vars and use real data ([`f2c4c28`](https://github.com/ESloman/bsebot/commit/f2c4c28d09b271a5ad31abfaf19613d70b207085))

* Add the task for sending the &#34;eddie gain&#34; messages. ([`922998f`](https://github.com/ESloman/bsebot/commit/922998f09876ead95c9f14f90647b34e3d63f479))

* Commit beginnings of passive eddie distribution ([`1116f92`](https://github.com/ESloman/bsebot/commit/1116f925f977a05f2fe396f5888e5616188cf91d))

* Begin adding logic to log every message in the server ([`9365bd9`](https://github.com/ESloman/bsebot/commit/9365bd9f270cb23cd2bd4a488a9d7c5bebd792ef))

* Actually commit right thing this time. ([`2b06a4a`](https://github.com/ESloman/bsebot/commit/2b06a4a1f5f00e3bf42e2d7cd88ed90728691d38))

* Enable command syncing ([`c9deb0f`](https://github.com/ESloman/bsebot/commit/c9deb0fc36704165e08122f74f13efcaf0bc233b))

* Allow users to provide timeout in command ([`464ddb3`](https://github.com/ESloman/bsebot/commit/464ddb3a53d3ef4fa0918f91be2dd65b0133ee8c))

* Add functionality to message losers/winners when a bet is closed. ([`8e63942`](https://github.com/ESloman/bsebot/commit/8e63942fe89bcf14356543bce68e03aac60f1ea1))

* Add regular task to check for &#34;expired bets&#34;
Add default timeout of 5 minutes to bets ([`5837622`](https://github.com/ESloman/bsebot/commit/58376221437faf69aa728ff7909e286a2072a9de))

* Upgraded to latest discord_slash
Added framework for up to four options in bets
Changed default emojis for two option bets
Enable both on_reaction_add and on_raw_reaction_add. The latter only fires if the message_id isn&#39;t in the cache
Fix a bug where reacting to anything by anyone would trigger the reaction event ([`9798f86`](https://github.com/ESloman/bsebot/commit/9798f86036ad2fa803c1e774aaa0f099a634c2fc))

* Switch out &#39;on_reaction_add&#39; to &#39;on_raw_reaction_add&#39;
Add &#39;bseddies active&#39; command to list active bets
Add client to the BaseEvent class ([`06b8bfe`](https://github.com/ESloman/bsebot/commit/06b8bfe797adfdaf0e4290714dab411b27e7e19d))

* Every entry should be on a new line ([`0a61e66`](https://github.com/ESloman/bsebot/commit/0a61e66bd914e416131649764b8e58907eadf49b))

* Beginning OOP-ing of slash commands.
Reformat leaderboard table.
Add in reaction to leaderboard table again. ([`aabaa18`](https://github.com/ESloman/bsebot/commit/aabaa18c91af5a58e573e0ed12551700ce48c3d2))

* Prevent users from gifts bots eddies ([`00c868f`](https://github.com/ESloman/bsebot/commit/00c868f7f4ad42b24e3213b67a70d94f3ef1a875))

* Use ctx.send rather than ctx.channel.send for ephemeral messages in this command ([`0e40222`](https://github.com/ESloman/bsebot/commit/0e40222cf7037e9bc029a110be7bd745e6c6e31a))

* Move the &#34;main&#34; code into __name__ == &#34;__main__&#34; block.
Added the &#34;gift eddies&#34; command
Ensure slash commands aren&#39;t global ([`22d586a`](https://github.com/ESloman/bsebot/commit/22d586ae2f6cec8bb829e218f50aa88e6121ab30))

* Updated implementation of BETA_MODE to look for env key. If we have a valid key then we&#39;re running debug and use test IDs. If we don&#39;t - then we&#39;re in BETA_MODE and running on the AWS instance. ([`29d591a`](https://github.com/ESloman/bsebot/commit/29d591a3417938e1fc17abb1df3684926f409672))

* Beginnings of making everything a bit more OOP. This is a bit of a mess but a work in progress.
Added some ephemeral and DM messages for errors on common items.
Added BETA_MODE flag. ([`ed6f698`](https://github.com/ESloman/bsebot/commit/ed6f698bac0c9eb7f8a1a596d8daec91dc989b08))

* Make sure only those who bet on the correct outcome get eddies ([`ec139e6`](https://github.com/ESloman/bsebot/commit/ec139e6b2dd5c9a52f5f4737ded96b41f3076c82))

* Fix mongo issues ([`a540f5e`](https://github.com/ESloman/bsebot/commit/a540f5e4fb4d4e41e09d54ebd331a83db7af572e))

* Commit BETA features. This includes:
- creating bets
- counting points placed on a bet
- closing a bet
- placing a bet
- viewing points
- viewing the leaderboard ([`42a3b28`](https://github.com/ESloman/bsebot/commit/42a3b28d66a1f533f193704032cecb7977a17557))

* Update default mongo port ([`99fa088`](https://github.com/ESloman/bsebot/commit/99fa088183fb80ec660d27b499d4eb44756f4afe))

* First commit.
- Basic mongo interface / db classes / collection classes for point storage
- Basic bot script that registers some slash commands and performs some actions ([`1d2cb16`](https://github.com/ESloman/bsebot/commit/1d2cb16013579c4caaa697330ac0a1c4a40181c8))

* Update .gitignore to hide .idea files ([`0f7c441`](https://github.com/ESloman/bsebot/commit/0f7c4416fdcf56fb500c379857c3d586d973ead4))

* Initial commit ([`5022b34`](https://github.com/ESloman/bsebot/commit/5022b343a49b47b16a521dcf744349df988a6149))