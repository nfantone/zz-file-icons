"use strict";

var gulp = require("gulp");
var color = require("color");
var path = require("path");
var fs = require("fs");
var merge = require("merge-stream");
var $ = require("gulp-load-plugins")();

var opts = {};

opts.colors = require("./common/colors.json");
opts.sizes = require("./common/sizes.json");

var getIconOpts = function() {
  return JSON.parse(fs.readFileSync("./common/icons.json", "utf8"));
};

var build_multi = function() {
  var baseColor = $.recolorSvg.ColorMatcher(color("#000"));

  opts.icons = getIconOpts();

  return gulp.src("./common/assets/*.svg")
    .pipe($.plumber(function(error) {
      console.log("[build:icons]".bold.magenta + " There was an issue rasterizing icons:\n".bold.red + error.message);
      this.emit("end");
    }))
    .pipe($.changed("./icons/multi", {extension: ".png"}))
    .pipe($.flatmap(function(stream, file) {
      var iconName = path.basename(file.path, path.extname(file.path));
      var iconOpts = opts.icons[iconName];
      var iconColor = color(opts.colors[iconOpts["color"]]);
      var iconImages = merge();

      iconImages.add(opts.sizes.map(function(size) {
        var multi = gulp.src(file.path)
          .pipe($.recolorSvg.Replace(
            [baseColor],
            [iconColor]
          ))
          .pipe($.svg2png({
            width: size.size,
            height: size.size
          }))
          .pipe($.if(size.size, $.rename({suffix: size.suffix})))
          .pipe($.imagemin([$.imagemin.optipng({
            bitDepthReduction: false,
            colorTypeReduction: false,
            paletteReduction: false
          })], {verbose: true}))
          .pipe(gulp.dest("./icons/multi"));
        return multi;
      }));

      return iconImages;
    }));
};

var build_single = function() {
  var baseColor = $.recolorSvg.ColorMatcher(color("#000"));

  opts.icons = getIconOpts();

  return gulp.src("./common/assets/*.svg")
    .pipe($.plumber(function(error) {
      console.log("[build:icons]".bold.magenta + " There was an issue rasterizing icons:\n".bold.red + error.message);
      this.emit("end");
    }))
    .pipe($.changed("./icons/single", {extension: ".png"}))
    .pipe($.flatmap(function(stream, file) {
      var iconColor = color("white");
      var iconImages = merge();

      iconImages.add(opts.sizes.map(function(size) {
        var single = gulp.src(file.path)
          .pipe($.recolorSvg.Replace(
            [baseColor],
            [iconColor]
          ))
          .pipe($.svg2png({
            width: size.size,
            height: size.size
          }))
          .pipe($.if(size.size, $.rename({suffix: size.suffix})))
          .pipe($.imagemin([$.imagemin.optipng({
            bitDepthReduction: false,
            colorTypeReduction: false,
            paletteReduction: false
          })], {verbose: true}))
          .pipe(gulp.dest("./icons/single"));
        return single;
      }));

      return iconImages;
    }));
};

gulp.task("multi", build_multi);

gulp.task("single", build_single);
