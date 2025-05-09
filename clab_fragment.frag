//precision mediump float;
#define PI 3.14159265359;


// currently unused...
//uniform float rando;
// the texCoords passed in from the vertex shader.
//varying vec2 v_texCoord;










// our texture
uniform sampler2D texture, mask;

// uniforms
// white and rgb coord based on color direction
uniform vec2 w_unif;
uniform vec2 rgb_unif;

// color space conversion matrixes
uniform mat3 rgb2xyz_unif;
uniform mat3 xyz2rgb_unif;
uniform mat3 xyz2lms_unif;
uniform mat3 lms2xyz_unif;

// max luminance for r,g,b pixels + sum
uniform vec3 lum_unifs;
float lum_sum = lum_unifs.r + lum_unifs.g + lum_unifs.b;

// desired TARGET LUMINANCE
uniform float targlum_unif;
float lum_mult = targlum_unif/lum_sum;

// experiment timer
uniform float time_unif;


//
// setting color space conversions
vec3 xyY_to_xyz(vec3 xyY) {
    float Y = xyY.z;
    float x = Y * xyY.x / xyY.y;
    float z = Y * (1.0 - xyY.x - xyY.y) / xyY.y;
    return vec3(x, Y, z);
}

vec3 xyz_to_xyY(vec3 xyz) {
    float Y = xyz.y;
    float x = xyz.x / (xyz.x + xyz.y + xyz.z);
    float y = xyz.y / (xyz.x + xyz.y + xyz.z);
    return vec3(x, y, Y);
}

// Converts a color from linear RGB to XYZ space
vec3 rgb_to_xyz(vec3 rgb) {
    return rgb2xyz_unif * rgb;
}

// Converts a color from XYZ to linear RGB space
vec3 xyz_to_rgb(vec3 xyz) {
    return xyz2rgb_unif * xyz;
}
// Converts a color from linear RGB to xyY space
vec3 rgb_to_xyY(vec3 rgb) {
    vec3 xyz = rgb_to_xyz(rgb);
    return xyz_to_xyY(xyz);
}

// Converts a color from xyY space to linear RGB
vec3 xyY_to_rgb(vec3 xyY) {
    vec3 xyz = xyY_to_xyz(xyY);
    return xyz_to_rgb(xyz);
}


vec3 xyz_to_lms(vec3 xyz) {
    return xyz2lms_unif * xyz;
}

vec3 lms_to_xyz(vec3 lms) {
    return lms2xyz_unif * lms;   //lms here is out of 1.0.
}

vec3 xyY_to_lms(vec3 xyY) {
    vec3 xyz = xyY_to_xyz(xyY);
    return xyz2lms_unif * xyz;
}

vec3 lms_to_xyY(vec3 lms) {
    vec3 xyz = lms2xyz_unif * lms;
    return xyz_to_xyY(xyz);
}

vec3 rgb_to_lms(vec3 rgb) {
    vec3 xyz = rgb_to_xyz(rgb);
    return xyz2lms_unif * xyz;
}

vec3 lms_to_rgb(vec3 lms) {
    vec3 xyz = lms2xyz_unif * lms;
    return xyz2rgb_unif * xyz;
}



float noi(vec2 p , float time_unif) {
    p.x = p.x + time_unif;
    p.y = p.y + time_unif;
    return fract(sin(dot(p.xy,vec2(12.9898,78.233))) * 43758.5453);
}




    // shader is saying
    // lets take the range from js-core (in terms of R,G,B or LM,Lum,SLM)
    // lets also make that vector transform from range to 4d vector in CIE. 

void main() {
    vec2 p = gl_TexCoord[0].st;
    vec4 texFrag = texture2D(texture,p);

    vec4 maskFrag = texture2D(mask,gl_TexCoord[1].st);
 
    float xval = w_unif.x + ((gl_Color.r) * (rgb_unif.x-w_unif.x));
    float yval = w_unif.y + ((gl_Color.r) * (rgb_unif.y-w_unif.y));


    // ( gl_color.g(0-1)  *  60 ) / 60...
    // lum_sum is same scale and unit as lum_unifs. 
    vec3 rgb_out = (xyY_to_rgb(vec3(xval, yval, gl_Color.g*lum_sum))/lum_unifs) * lum_mult;




    // noisy bit. 
    //rgb_out += vec3((noi(p,time_unif/1000.0)-0.5)/255.0, (noi(p+0.1,time_unif/1000.0)-0.5)/255.0, (noi(p+0.2,time_unif/1000.0)-0.5)/255.0);   // currently noi(p,0.0), where 0 should be time. 
    rgb_out += vec3((noi(p,time_unif)-0.5)/255.0, (noi(p+0.1,time_unif)-0.5)/255.0, (noi(p+0.2,time_unif)-0.5)/255.0);   // currently noi(p,0.0), where 0 should be time. 

    gl_FragColor.rgb = rgb_out;
    gl_FragColor.a = gl_Color.a * texFrag.a * maskFrag.a; 



}



//
//
//
//
//
// NOTE
// so multiplying color_g by sum of r,g,b max luminances (white luminance),
// then dividing output RGB by max luminance of each r,g,b normalizes to main_code -1.0 to 1.0. 