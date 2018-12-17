# [![A File Icon][img-logo]][downloads]

[![Star on GitHub][img-stars]][stars]
[![Join the chat at Sublime Forum][img-forum]][forum]

This package adds file-specific icons to Sublime Text for improved visual grepping. It's heavily inspired by [Atom File Icons](https://github.com/file-icons/atom).

Its aims are:

* To be a `tmPreferences` storage for UI themes those support file-specific icons.
* To provide icons for themes those don't (fully) support file-specific icons.

If you have any problems, please search for a similar issue first, before creating [a new one][new-issue]. 

> Also, check the list of [known issues][known-issues] before doing so.

## Users

### Installation

#### Package Control

The easiest way to install is using Sublime's [Package Control][downloads]. It's listed as `A File Icon`.

1. Open `Command Palette` using menu item `Tools → Command Palette...`
2. Choose `Package Control: Install Package`
3. Find `A File Icon` and hit `Enter`

#### Download

1. [Download the `.zip`][release]
2. Unzip and rename folder to `A File Icon`
3. Copy folder into `Packages` directory, which you can find using the menu item `Preferences → Browse Packages...`

> **Note:** Don't forget to restart Sublime Text after installing this package. 

### Customization

You can change the color, opacity level and size of the icons by modifying your user preferences file, which you can find by:

* `Preferences → Package Settings → A File Icon → Settings`,
* Choose `A File Icon: Settings` in `Command Palette`.

### Wrong Icons

Sublime Text uses syntax scopes for file-specific icons. That's why icons of packages provided by the community require them to be installed.

See the list of [community packages][packages] that you may need to install to see the right icon.

### Themes

If your theme supports an icon customization you can choose what icons you want to use – provided by the theme (by default) or provided by the package. Otherwise this package adds its own icons only.

### Troubleshooting

If something goes wrong try to:

1. Open `Command Palette` using menu item `Tools → Command Palette...`.
2. Choose `A File Icon: Revert to a Freshly Installed State`.
3. Restart Sublime Text.

## Developers

### Bring Support of the File Icon Customization to Your Theme

If you are a theme developer and you want to support a file icon customization, you should:

* Remove all stuff related to the icon setup: `.tmPreferences`, `.sublime-settings`, `.sublime-syntax` and `.tmLanguage` files.
* Rename all your existing icons to match [these ones][icons].
* Add `.supports-a-file-icon-customization` file to the root of your theme (this is how we check if the theme **supports** customization of the file-specific icons).

### How It Works

In simple terms, `A File Icon` does the following:

1. Copies all the necessary files right after install or upgrade to `zzz A File Icon zzz` directory
2. Searches all installed themes
3. Checks if themes are already patched, if not
4. Patches them by generating `<theme-name>.sublime-theme` files from a [template][template]
5. For themes those support file icon customization, it provides `.tmPreferences` files and missing icons by default (user can override icons provided by the theme via `"force_mode": true`).

The real process is just a little bit more complex to minimize hard drive I/O.

## Resources

### Colors

Colors are bright because they should look good with most themes. However you can change color and opacity level of all icons. See [customization][customization].

![Palette][img-palette]

### Icons

This package contains icons provided by:

- [Atom File Icons](https://github.com/file-icons/atom)
- [Devicons](http://vorillaz.github.io/devicons/#/main)
- [Font Awesome](http://fontawesome.io/)
- [Font Mfizz](http://fizzed.com/oss/font-mfizz)
- [Icomoon](https://icomoon.io/)
- [Octicons](https://octicons.github.com/)

Source icons are provided in SVG format (Sublime Text doesn't currently support it). We convert them to @1x and @2x PNG assets before each release via a custom `gulp` task. 

Rasterized icons can be found in `icons` folder.

<!-- Misc -->

[customization]: https://github.com/deathaxe/sublime-a-file-icon#customization
[downloads]: https://packagecontrol.io/packages/A%20File%20Icon 'A File Icon @ Package Control'
[forum]: https://forum.sublimetext.com/t/a-file-icon-sublime-file-specific-icons-for-improved-visual-grepping/25874
[icons]: https://github.com/deathaxe/sublime-a-file-icon/tree/develop/icons/multi
[known-issues]: https://github.com/deathaxe/sublime-a-file-icon/labels/known%20issue
[new-issue]: https://github.com/deathaxe/sublime-a-file-icon/issues/new
[packages]: https://github.com/deathaxe/sublime-a-file-icon/blob/develop/PACKAGES.md
[release]: https://github.com/deathaxe/sublime-a-file-icon/releases
[stars]: https://github.com/deathaxe/sublime-a-file-icon/stargazers
[template]: https://github.com/deathaxe/sublime-a-file-icon/blob/develop/common/templates/theme.py
[issues]: https://github.com/deathaxe/sublime-a-file-icon/issues

<!-- Assets -->

[img-forum]: media/reply-on-forum.svg
[img-getting-started]: media/getting-started.jpg
[img-logo]: media/logo.png
[img-palette]: media/palette.png
[img-stars]: media/star-on-github.svg
