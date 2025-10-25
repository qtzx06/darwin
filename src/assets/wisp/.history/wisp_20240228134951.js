/**
 * Author: Ryan The Developer
 * Description: This file contains the code for the wisp animation.
 * The wisp animation is a particle system that uses a shader to simulate the movement of the particles.
 * The particles are rendered as points and are colored using a gradient texture.
 * The particles are moved using a shader that uses Perlin noise to simulate the movement of the particles.
 * The particles are colored using a gradient texture that is generated using a color palette.
 * The color palette is generated using a list of color references.
 * The color palette is used to color the particles based on their position in the gradient texture.
 * The particles are rendered using a shader that uses the gradient texture to color the particles.

* https://www.ryanthedeveloper.com/
* https://www.youtube.com/channel/UCeGt43CPg9o0XlPebjZie9Q/
* https://twitter.com/ryan_the_dev
* https://www.instagram.com/ryan_the_dev/
* https://www.instagram.com/ryan_the_developer/
 */

// Importing specific functionalities from the Three.js library to be used for graphics rendering.
// These imports include classes for materials, geometries, textures, and more, facilitating the creation of custom shaders, handling of geometries, textures, and particles.
import {
  AdditiveBlending, // For additive blending of colors.
  BufferAttribute, // To create custom attributes for geometry, like positions.
  BufferGeometry, // The base class for geometries used in points, lines, and meshes.
  Color, // To handle color operations.
  DataTexture, // For creating textures directly from data.
  FloatType, // Defines the type of values stored in a texture (floating point).
  GLSL3, // Specifies the GLSL version to use in shaders.
  LinearFilter, // Used for texture filtering. Linear for smooth transitions.
  NearestFilter, // Another type of texture filtering. Picks the nearest pixel.
  Points, // For rendering particles as points.
  RGBAFormat, // Texture format that includes red, green, blue, and alpha channels.
  RawShaderMaterial, // Material that allows for the creation of custom shaders.
  UnsignedByteType, // Defines the data type in a texture (8-bit unsigned integer).
} from "../third_party/three.module.js";

// Importing custom shader code and utility functions.
import { mod, randomInRange } from "../modules/Maf.js"; // Math utilities for modulus operation and generating random numbers within a range.
import { ShaderPingPongPass } from "../modules/ShaderPingPongPass.js"; // A utility for performing shader operations back and forth between two textures.
import { shader as curl } from "../shaders/curl.js"; // Custom shader for generating curl noise.
import { shader as noiseCommon } from "../shaders/noise-common.js"; // Common noise functions used across different shaders.
import { shader as noise2d } from "../shaders/noise2d.js"; // Shader for generating 2D noise patterns.
import { shader as noise3d } from "../shaders/noise3d.js"; // Shader for generating 3D noise patterns.
import { shader as orthoVs } from "../shaders/ortho.js"; // Shader for orthographic (non-perspective) rendering.

// Array of hexadecimal color values organized in sub-arrays. Each sub-array represents a color palette.
const refs = [
    // Each sub-array contains hex values for colors.
  [2967132, 3170409, 4671067, 15911601],
  [13461288, 8879740, 9083045, 14340540],
  [8544560, 9333301, 16699532, 16765583],
  [3103077, 10006951, 15965066, 15904924, 15911601],
  [3033437, 9809829, 15961727, 13489090, 15911087],
  [5587489, 11110993, 13868883, 16765583],
  [10517571, 13343827, 15840097, 16765583],
  [10179625, 9068616, 15178571, 13946298],
  [2966619, 3103334, 15911601, 15911601],
  [4530186, 7550731, 14650692, 15771228],
  [4721927, 4721927, 4918278, 5901318, 16558112, 9817289],
  [7604996, 15433495, 16498260, 9817289, 16567714],
  [3473408, 5374977, 10651460, 15559189, 13088113],
  [4719360, 11370015, 14962958, 15357455, 16249260],
  [4721927, 1676705, 13648395, 16681522, 14473124],
  [4721927, 4721927, 1085854, 4235676, 16496709],
  [4721927, 3711915, 7123102, 16679975, 16507333],
  [4721927, 7801604, 16559661, 16309143, 16113829],
  [7691087, 16486192, 12359802],
  [5508637, 12345129, 16692073, 16563839],
  [7284775, 9923966, 9468310, 15234599, 16692073],
  [5589910, 16137325, 13671093, 15510716, 16709346],
  [7035549, 16423860, 15510716],
  [9715564, 16561152, 15216436],
  [5786517, 9926311, 15510716, 15510716],
  [7692704, 9532070, 15510716, 16704934, 16492991],
  [7626911, 16489480, 16420109, 15510716],
  [1188974, 815571, 1082845, 1149663, 15759921, 15059646],
  [1462196, 11024936, 881876, 16015874, 15059645],
  [548041, 548297, 11575599],
  [7553371, 749009, 15822621, 13489380],
  [734337, 2833534, 1216225, 16016899],
  [6701927, 938400, 482248, 12804628],
  [665717, 5719413, 3689108, 682191, 11575599, 11575599],
  [869523, 1008307, 748240, 9345469],
  [2504571, 10959401, 11575599, 15059388],
  [1145290, 815058, 11575599, 5135764],
  [733053, 3556996, 16353806, 16556308, 15441779],
  [8143997, 16143391, 16206455, 15510716, 15510716],
  [9322608, 13906753, 15543857, 10714538, 16134758, 16424630],
  [7692704, 8875172, 12554161, 16633689, 16279180, 15510716],
  [9388143, 9138085, 16072486, 16562634],
];

// Function to randomly choose a color palette from the `refs` array and prepare it for use in the shader.
function randomizePalette() {
  const ref = refs[Math.floor(Math.random() * refs.length)]; // Randomly select a palette.
  let colors = ref.map((v) => new Color().setHex(v)); // Convert hex values to Color objects.

  const bkg = colors[0].clone(); // Clone the first color for the background.
  const t = new Color();
  bkg.getHSL(t); // Convert the background color to HSL.
  // t.h -= 0.1; // Adjust hue by -0.1 (commented out).
  t.s /= 2; // Halve the saturation.
  t.l /= 2; // Halve the lightness.
  bkg.setHSL(t.h, t.s, t.l); // Apply the adjusted HSL values back to the background color.

  // Prepare a Uint8Array to hold color data for a gradient texture.
  const gradientData = new Uint8Array(colors.length * 4);
  for (let i = 0; i < colors.length; i++) {
    const c = colors[i]; // Current color.
    // Fill the array with color data: red, green, blue, and alpha (fully opaque).
    gradientData[i * 4] = c.r * 255;
    gradientData[i * 4 + 1] = c.g * 255;
    gradientData[i * 4 + 2] = c.b * 255;
    gradientData[i * 4 * 3] = 1 * 255; // Alpha channel (fully opaque).
  }
  // Create a DataTexture from the gradient data.
  const gradientTex = new DataTexture(
    gradientData,
    colors.length, // Width of the texture.
    1, // Height of the texture (1 for a gradient).
    RGBAFormat,
    UnsignedByteType,
    undefined, // Default settings for the rest.
    undefined,
    undefined,
    LinearFilter, // Smooth out the gradient.
    LinearFilter
  );
  gradientTex.needsUpdate = true; // Mark the texture as needing an update.
  return { bkg, gradientTex }; // Return the background color and the gradient texture.
}

// GLSL code snippets for calculating particle positions and rendering.
// getHeight: GLSL function to compute height based on 3D noise.
const heightFn = `
float getHeight(in vec3 point) {
  vec3 point2 = (point * 1. + 123. + time) * .8;
  float perlin1 = noise3d(point + offset);
  float perlin2 = noise3d(point2 - offset);
  return mix(perlin1, perlin2, .5);
}

vec3 getPoint(in vec3 p, out float n) {
  n = getHeight(p*1.);
  return p + normalize(p)* n * 5.;
}`;

// Vertex shader for particles.
// Defines how particle positions are calculated and how they're rendered.
// Includes custom noise functions for dynamic effects.
// This shader, identified as `particleVs`, is a vertex shader written in GLSL (OpenGL Shading Language) for rendering particles in a 3D graphics application, specifically designed to work within a WebGL context provided by Three.js or similar frameworks. Vertex shaders are executed for each vertex in the mesh to compute its position and other per-vertex data. Here's a detailed breakdown of its components and functionality:

//  Shader Precision
// - `precision highp float;`: Sets the precision for floating-point operations to high, which is necessary for mathematical calculations in the shader, ensuring accuracy and avoiding artifacts in the rendering process.

//  Inputs
// - `in vec3 position;`: The input vertex position. In the context of particles, each position likely represents the center of a particle.

//  Uniforms
// - `uniform sampler2D positions;`: A 2D texture that stores positions for particles. Each texel (texture pixel) contains data for a specific particle.
// - `uniform sampler2D gradient;`: A 2D texture used for applying color gradients to particles based on some criteria, such as their age or velocity.
// - `uniform float dpr;`: Device Pixel Ratio. This is used to adjust the size of the rendered particles so they appear consistent across devices with different pixel densities.
// - `uniform float time;`: A uniform that likely represents the elapsed time or a timestamp used in animations or dynamic effects within the shader.
// - `uniform vec3 bkgColorFrom;`: Starting color of a background color transition.
// - `uniform vec3 bkgColorTo;`: Ending color of a background color transition.
// - `uniform float interpolate;`: A factor used to interpolate between `bkgColorFrom` and `bkgColorTo`, possibly for animating the background color or other properties over time.
// - `uniform float offset;`: A general-purpose offset, potentially used in positioning or animating the particles.
// - `uniform mat4 modelViewMatrix;`: The model-view matrix used to transform vertex positions from model space to view space.
// - `uniform mat4 projectionMatrix;`: The projection matrix used to project the view-space coordinates of the vertices onto the screen.

//  Outputs
// - `out float vGradientIndex;`: Custom output variable that may be used to pass the gradient index from the vertex shader to the fragment shader, determining which part of the gradient texture to use for coloring each particle.
// - `out float vLife;`: Another custom output variable, possibly intended to pass a life value or age of each particle from the vertex shader to the fragment shader, but it's not assigned in this shader, indicating it might be used or assigned elsewhere or in an omitted part of the code.

//  Shader Code Inclusion
// - `${noiseCommon}`, `${noise3d}`, and `${heightFn}`: These placeholders suggest that common noise functions, 3D noise functions, and a custom function for calculating height are injected into the shader code. This technique allows for modularity and reusability of shader code across different shaders.

//  Main Function
// - `void main() { ... }`: The main execution function of the shader where the processing of vertex positions and other computations occur.
//     - `vec2 coord = position.xy;`: Extracts the x and y components from the input position to use as texture coordinates.
//     - `vec4 pos = texture(positions, coord);`: Samples the `positions` texture using `coord` to retrieve the position and potentially other data encoded in the texture for a particle.
//     - `float n; vec3 newPos = getPoint(pos.xyz, n);`: Calls a custom function `getPoint`, likely defined in `${heightFn}`, to compute a new position for the vertex based on its original position and possibly influenced by noise to create effects like waving or displacement.
//     - `gl_Position = projectionMatrix * modelViewMatrix * vec4(newPos.xyz, 1.);`: Calculates the final position of the vertex in clip space by transforming `newPos` using the model-view and projection matrices.
//     - `vGradientIndex = pos.w / 100.;`: Assigns a value to `vGradientIndex`, possibly mapping the w component of the `pos` to a range within the gradient texture.
//     - `gl_PointSize = 6. * dpr;`: Sets the size of the rendered point (particle) dynamically based on the device pixel ratio, ensuring consistent visual appearance across different screen resolutions.

// This shader is part of a larger system for rendering particles with dynamic positions, sizes, and colors based on textures, noise, and time-based animations. The exact visual outcome would depend on the specific implementations of the noise functions and other custom code not shown here.
const particleVs = `precision highp float;
in vec3 position;

uniform sampler2D positions;
uniform sampler2D gradient;
uniform float dpr;
uniform float time;
uniform vec3 bkgColorFrom;
uniform vec3 bkgColorTo;
uniform float interpolate;
uniform float offset;

uniform mat4 modelViewMatrix;
uniform mat4 projectionMatrix;

out float vGradientIndex;
out float vLife;

${noiseCommon}
${noise3d}

${heightFn}

void main() {
  vec2 coord = position.xy;
  vec4 pos = texture(positions, coord);
  float n;
  vec3 newPos = getPoint(pos.xyz, n);
  gl_Position = projectionMatrix * modelViewMatrix * vec4(newPos.xyz, 1.);
  vGradientIndex = pos.w / 100.;
  gl_PointSize = 6. * dpr;
}`;



const movingParticleVs = `
// Specifies the precision of float types. 'highp' indicates high precision, necessary for positions and calculations requiring accuracy.
precision highp float;

// Input attributes from the particle geometry. Each particle's position is a 3D vector.
in vec3 position;

// Uniforms are parameters that are the same for all vertices processed by the shader.
uniform sampler2D positions; // Texture containing position data for particles.
uniform float dpr; // Device Pixel Ratio for rendering on different screen resolutions.
uniform mat4 modelViewMatrix; // Matrix to transform vertices from model to view space.
uniform mat4 projectionMatrix; // Matrix to project 3D coordinates to 2D screen space.

// Outputs to the fragment shader.
out float vGradientIndex; // Used to determine which color to use from the gradient.
out float vLife; // Life value of the particle, not used in this shader but declared for compatibility.

// A function to create a parabolic effect, used to modify particle size.
float parabola(in float x, in float k) {
  return pow(4. * x * (1. - x), k);
}

// Main function where the processing of each vertex happens.
void main() {
  vec2 coord = position.xy; // Extracts the x and y components of the position.
  vec4 pos = texture(positions, coord); // Retrieves the particle's position from the texture.
  
  // Calculates the final position of the vertex by transforming it with the model-view and projection matrices.
  gl_Position = projectionMatrix * modelViewMatrix * vec4(pos.xyz, 1.);
  
  // Extracts the gradient index from the w component of the texture, scaled by 1/100.
  vGradientIndex = pos.w/100.;
  
  // Dynamically calculates the point size based on the w component of the position and the device pixel ratio.
  gl_PointSize = (1. - (pos.w / 100.)) * 6. * dpr * position.z;
}

`;

const particleFs = `
// Specifies the precision for floating point numbers. High precision is used for color and coordinate calculations.
precision highp float;

// Inputs from the vertex shader.
in float vLife; // The life value of the particle, affects the particle's transparency or color in some shaders.
in float vGradientIndex; // The index to look up in the gradient textures.

// Uniforms are parameters that are the same for all fragments processed by the shader.
uniform sampler2D gradientFrom; // The starting gradient texture.
uniform sampler2D gradientTo; // The ending gradient texture.
uniform float interpolate; // A value used to interpolate between the starting and ending gradients.

// The output color of the fragment.
out vec4 fragColor;

// Main function where the color for each fragment is determined.
void main() {
  // Converts the point coordinate to a circular domain and discards fragments outside the circle to create a round particle.
  vec2 circCoord = 2.0 * gl_PointCoord - 1.0;
  if (dot(circCoord, circCoord) > 1.0) {
    discard; // Discards the fragment if it's outside the circle, making the particle round.
  }
  
  // Prepares the texture coordinate for gradient lookup, using the gradient index.
  vec2 guv = vec2(vGradientIndex, .5);
  
  // Fetches the colors from the start and end gradients based on the gradient index.
  vec3 from = texture(gradientFrom, guv).xyz;
  vec3 to = texture(gradientTo, guv).xyz;
  
  // Interpolates between the start and end colors based on the 'interpolate' uniform.
  vec3 color = mix(from, to, interpolate);
  
  // Sets the fragment color, with an alpha value of .15 for some transparency.
  fragColor = vec4(color, .15);

}`;
// Define the width and height for the texture. In this case, it's a square texture of 512x512 pixels.
const width = 512;
const height = 512;

// Initialize a Float32Array to hold the position data. 
// The size is width * height * 4 because each point has an (x, y, z) coordinate plus an extra value (e.g., for random data), making 4 values per point.
const posData = new Float32Array(width * height * 4);

// Initialize a pointer to keep track of the current position in the posData array.
let ptr = 0;

// Radius for the spherical coordinates. Set to 1, which will normalize the positions.
const r = 1;

// Iterate over each pixel in the texture.
for (let y = 0; y < height; y++) {
  for (let x = 0; x < width; x++) {
    // Generate spherical coordinates.
    const phi = Math.acos(2 * Math.random() - 1) - Math.PI / 2; // Phi angle for the spherical coordinates.
    const theta = 2 * Math.PI * Math.random(); // Theta angle for the spherical coordinates.
    
    // Convert spherical coordinates to Cartesian coordinates for the 3D position.
    posData[ptr] = r * Math.cos(phi) * Math.cos(theta); // X coordinate.
    posData[ptr + 1] = r * Math.cos(phi) * Math.sin(theta); // Y coordinate.
    posData[ptr + 2] = r * Math.sin(phi); // Z coordinate.
    
    // Store a random value in the fourth component of the position data.
    posData[ptr + 3] = randomInRange(0, 100); // Random value, potentially used for attributes like size, opacity, etc.
    
    // Move the pointer ahead by 4 to the next position in the array.
    ptr += 4;
  }
}

// Create a Three.js DataTexture using the generated position data.
const posTexture = new DataTexture(
  posData, // The position data array.
  width, // Texture width.
  height, // Texture height.
  RGBAFormat, // Texture format, indicating each pixel has four components (red, green, blue, alpha).
  FloatType, // Type of the data in the texture (32-bit floating point numbers).
  undefined, // No mipmapping.
  undefined, // Texture wrapping in the S (U) direction.
  undefined, // Texture wrapping in the T (V) direction.
  NearestFilter, // Minification filter.
  NearestFilter // Magnification filter.
);

// Mark the texture as needing an update the next time it's used.
posTexture.needsUpdate = true;


  const simFs = `
  // Specifies that high precision should be used for floating-point and sampler3D types.
precision highp float;
precision highp sampler3D;

// Input UV coordinates from the vertex shader.
in vec2 vUv;

// Uniforms are global variables set for each shader invocation.
uniform sampler2D inputTexture; // Texture storing current particle positions or states.
uniform sampler2D originTexture; // Initial or reference texture for particle positions or states.
uniform float persistence; // Could be used for effects that require persistence over time.
uniform float time; // Current time, likely used for animation and dynamics.
uniform float dt; // Delta time, representing the change in time between frames.
uniform float offset; // An offset value, potentially used for noise calculation or position adjustments.

// Output color of the fragment.
out vec4 fragColor;

// Shader code for noise and other functions, injected as strings.
${noiseCommon}
${curl}
${noise3d}
${noise2d}
${heightFn}

// Main function of the shader.
void main() {
  vec4 pos = texture(inputTexture, vUv); // Fetch the current position from the input texture.
  float n; // Variable to store noise or other calculated values.

  pos.w += dt; // Increment the w-component (could represent time or age) of the position by delta time.
  if(pos.w>100.) { // Reset the w-component and position if a certain condition is met.
    pos.w -= 100.;
    pos.xyz = texture(originTexture, vUv).xyz; // Reset position to the original state.
    pos.xyz = getPoint(normalize(pos.xyz), n); // Apply a transformation to the reset position.
  }

  // Apply noise and other transformations to the position.
  pos.xyz = pos.xyz + .05 * normalize(curlNoise(pos.xyz * .1 + offset, time)) + .01 * vec3(snoise(pos.xy), snoise(pos.yz), snoise(pos.xz));
  vec3 t = getPoint(normalize(pos.xyz), n); // Recalculate the position after applying noise.
  if(length(t.xyz) > length(pos.xyz)) {
    pos.xyz = t.xyz; // Update the position if a certain condition is met, based on the calculated lengths.
  }

  fragColor = pos; // Set the fragment color to the updated position value.
}

  
  `;
  // This part sets up the shader material in Three.js:
  const simShader = new RawShaderMaterial({
    uniforms: { // Define uniform variables for the shader.
      inputTexture: { value: posTexture }, // Current state texture.
      originTexture: { value: posTexture }, // Original state texture.
      persistence: { value: 1 }, // Placeholder value for persistence.
      time: { value: 0 }, // Initial time value.
      offset: { value: 0 }, // Initial offset value.
      dt: { value: 0 }, // Initial delta time value.
    },
    vertexShader: orthoVs, // Vertex shader for setting up positions.
    fragmentShader: simFs, // The fragment shader defined above.
    glslVersion: GLSL3, // Specify the GLSL version.
  });
  
  // This material is used for rendering the particles with the computed positions from the simulation:
  const simulation = new ShaderPingPongPass(simShader, {
    format: RGBAFormat, // Texture format.
    type: FloatType, // Data type of the texture.
    minFilter: NearestFilter, // Minification filter.
    magFilter: NearestFilter, // Magnification filter.
  });
  simulation.setSize(width, height); // Set the size of the simulation.
  

  const material = new RawShaderMaterial({
    uniforms: { // Uniforms for the particle shader, including textures and parameters for rendering.
      positions: { value: posTexture },
      time: { value: 0 },
      offset: { value: 0 },
      dpr: { value: 1 },
      gradientFrom: { value: null },
      gradientTo: { value: null },
      bkgColorFrom: { value: new Color() },
      bkgColorTo: { value: new Color() },
      interpolate: { value: 0 },
    },
    vertexShader: particleVs, // Vertex shader for particles.
    fragmentShader: particleFs, // Fragment shader for particle coloring.
    glslVersion: GLSL3, // GLSL version.
    transparent: true, // Enable transparency.
    blending: AdditiveBlending, // Use additive blending for the particles.
  });
  

  
// Create a new buffer geometry object to hold vertices of particles.
const geo = new BufferGeometry();

// Create a flat array to store position data for each vertex.
const vertices = new Float32Array(width * height * 3);

// Initialize a pointer to keep track of the current position in the vertices array.
ptr = 0;

// Loop through each "pixel" to compute and assign positions for each particle.
for (let y = 0; y < height; y++) {
  for (let x = 0; x < width; x++) {
    // Normalize x and y positions and assign a random z position between 1 and 2.
    vertices[ptr] = x / width; // X position normalized.
    vertices[ptr + 1] = y / width; // Y position normalized.
    vertices[ptr + 2] = randomInRange(1, 2); // Z position randomized.
    ptr += 3; // Move to the next set of positions.
  }
}

// Assign computed vertices to the geometry as the position attribute.
geo.setAttribute("position", new BufferAttribute(vertices, 3));

// Create a Points object using the geometry and a material for rendering.
const mesh = new Points(geo, material);

// Define a second material using RawShaderMaterial for customized shader programming.
const material2 = new RawShaderMaterial({
  // Uniforms are global variables passed to shaders.
  uniforms: {
    positions: { value: posTexture }, // Position texture.
    gradientFrom: { value: null }, // Start gradient (to be defined).
    gradientTo: { value: null }, // End gradient (to be defined).
    interpolate: { value: 0 }, // Interpolation factor.
    dpr: { value: 1 }, // Device pixel ratio for resolution handling.
  },
  vertexShader: movingParticleVs, // Vertex shader for particle movement.
  fragmentShader: particleFs, // Fragment shader for particle appearance.
  glslVersion: GLSL3, // Specifies GLSL version.
  transparent: true, // Enables transparency.
  blending: AdditiveBlending, // Uses additive blending for visual effect.
});

// Repeat the process of creating a buffer geometry and vertices for a second particle system.
const geo2 = new BufferGeometry();
const vertices2 = new Float32Array(width * height * 3);
ptr = 0; // Reset pointer for new geometry.
// Loop to assign normalized positions and a random z value, similar to the first geometry setup.
for (let y = 0; y < height; y++) {
  for (let x = 0; x < width; x++) {
    vertices2[ptr] = x / width;
    vertices2[ptr + 1] = y / width;
    vertices2[ptr + 2] = randomInRange(1, 2);
    ptr += 3;
  }
}
// Assign these vertices to the second geometry.
geo2.setAttribute("position", new BufferAttribute(vertices2, 3));
const mesh2 = new Points(geo2, material2);

// Function to update shader uniforms based on time and render the simulation.
function step(renderer, t, dt) {
  // Update uniforms for the simulation shader.
  simulation.shader.uniforms.dt.value = dt;
  simulation.shader.uniforms.time.value = t;
  mesh.material.uniforms.time.value = t;
  // Render the current state of the simulation.
  simulation.render(renderer);
  // Update the input texture for the next frame.
  simulation.shader.uniforms.inputTexture.value = simulation.fbos[simulation.currentFBO].texture;
}

// Initialize variables for background color interpolation.
let bkgFrom, bkg = new Color(), paletteFrom;
let { bkg: bkgTo, gradientTex: paletteTo } = randomizePalette(); // Initial random palette.

// Function to update color gradients and background based on the random palette.
function randomizeColors() {
  // Update background and gradient colors.
  bkgFrom = bkgTo;
  paletteFrom = paletteTo;
  // Get a new random palette.
  let { bkg: b2, gradientTex: g2 } = randomizePalette();
  bkgTo = b2;
  paletteTo = g2;
  // Apply new colors to materials.
  material.uniforms.bkgColorFrom.value.copy(bkgFrom);
  material.uniforms.bkgColorTo.value.copy(bkgTo);
  material.uniforms.gradientFrom.value = paletteFrom;
  material2.uniforms.gradientFrom.value = paletteFrom;
  material.uniforms.gradientTo.value = paletteTo;
  material2.uniforms.gradientTo.value = paletteTo;
}

// Function to interpolate colors over time for a smooth transition.
let prevT = 0;
function interpolate(time, renderer) {
  let t = mod(time, 10000) / 10000; // Calculate a looping time factor.
  if (t < prevT) {
    randomizeColors(); // Update colors when looping restarts.
  }
  prevT = t; // Update previous time.
  // Apply interpolation factor to materials.
  material.uniforms.interpolate.value = t;
  material2.uniforms.interpolate.value = t;
  // Interpolate background color and update renderer background.
  bkg.copy(bkgFrom).lerp(bkgTo, t);
  renderer.setClearColor(bkg, 1);
}

// Export relevant entities for external use.
export {
  interpolate, mesh,
  mesh2, posTexture, randomizeColors, simulation, step
};
