// Import necessary components from Three.js for shader material, texture formats, vector types, and more.
import {
  ClampToEdgeWrapping,
  GLSL3,
  LinearFilter,
  RGBAFormat,
  RawShaderMaterial,
  UnsignedByteType,
  Vector2
} from "./third_party/three.module.js";

// Import utility functions and classes for frame buffer objects (FBOs), shader passes, and specific shaders for effects.
import { ShaderPass } from "./modules/ShaderPass.js";
import { BloomPass } from "./modules/bloomPass.js";
import { getFBO } from "./modules/fbo.js";
import { shader as levels } from "./shaders/levels.js";
import { shader as noise } from "./shaders/noise.js";
import { shader as orthoVertexShader } from "./shaders/ortho.js";
import { shader as screen } from "./shaders/screen.js";
import { shader as vignette } from "./shaders/vignette.js";

// Fragment shader for combining the rendered scene with various effects like blur, vignette, and noise.
const finalFragmentShader = `
precision highp float; // Sets high precision for floating point operations.

// Uniforms are global variables passed from JavaScript to shaders.
uniform vec2 resolution; // The resolution of the screen or render target.
uniform sampler2D inputTexture; // The original rendered scene texture.

// Textures containing blurred versions of the scene for bloom effect.
uniform sampler2D blur0Texture;
uniform sampler2D blur1Texture;
uniform sampler2D blur2Texture;
uniform sampler2D blur3Texture;
uniform sampler2D blur4Texture;

uniform float vignetteBoost; // Controls the strength of the vignette effect.
uniform float vignetteReduction; // Controls the amount of vignette reduction.

uniform float time; // A time value, could be used for animated effects.

in vec2 vUv; // The UV coordinates for the fragment.

out vec4 fragColor; // The output color of the fragment.

// Includes shader code as strings for effects to be applied.
${vignette}
${noise}
${screen}
${levels}

void main() {
  // Sample the blur textures at the current UV coordinate.
  vec4 b0 = texture(blur0Texture, vUv);
  vec4 b1 = texture(blur1Texture, vUv);
  vec4 b2 = texture(blur2Texture, vUv);
  vec4 b3 = texture(blur3Texture, vUv);
  vec4 b4 = texture(blur4Texture, vUv);
  
  // Sample the original scene texture.
  vec4 color = texture(inputTexture, vUv);

  // Combine blur textures with different weights for bloom effect.
  float s = 40.;
  vec4 b = b0 / s;
  b += 2. * b1 / s;
  b += 4. * b2 / s;
  b += 8. * b3 / s;
  b += 16. * b4 / s;

  // Apply screen blending, vignette, noise, and levels effects.
  fragColor = screen(color, b, 1.);
  fragColor *= vignette(vUv, vignetteBoost, vignetteReduction);
  fragColor += .01 * noise(gl_FragCoord.xy, time);
  fragColor.a = 1.;
  fragColor.rgb = finalLevels(fragColor.rgb, vec3(.2), vec3(1.), vec3(.8));
}
`;

// Fragment shader for applying a color effect based on the input texture and noise.
const colorFragmentShader = `precision highp float; // High precision for fragment calculations.

uniform sampler2D inputTexture; // The texture to apply the color effect to.
uniform float time; // Time value for animated effects.

in vec2 vUv; // UV coordinates of the fragment.

out vec4 fragColor; // Output color of the fragment.

${noise} // Include shader code for generating noise.

void main() {
  // Calculate the size of the input texture.
  vec2 size = vec2(textureSize(inputTexture, 0));
  int steps = 10; // Number of steps for the effect.
  float total = 0.; // Total weight for normalization.
  vec4 accum = vec4(0.); // Accumulator for the color effect.
  float fSteps = float(steps); // Convert steps to float for calculations.
  for(int i = 0; i < steps; i++){
    // Calculate incremental direction based on the loop index.
    vec2 inc = 20. * float(i) / (fSteps * size);
    vec2 dir = vUv - .5; // Direction vector from the center of the texture.
    // Sample the texture at different offsets for RGB channels.
    vec4 r = texture(inputTexture, vUv - dir * inc);
    vec4 g = texture(inputTexture, vUv);
    vec4 b = texture(inputTexture, vUv + dir * inc);
    // Weight for the current step.
    float w = float(steps - i) / fSteps;
    // Accumulate weighted color.
    accum += vec4(r.r, g.g, b.b, 0.) * w;
    total += w;
  }
  // Normalize the accumulated color.
  accum /= total;
  // Set the fragment color, adding noise for detail.
  fragColor = vec4(accum.rgb , 1.);
  fragColor += .01 * noise(gl_FragCoord.xy, time);
}`;

// The Post class encapsulates the post-processing pipeline.
class Post {
  constructor(renderer, params = {}) {
    this.renderer = renderer; // WebGL renderer from Three.js.

    // Create a frame buffer object for offscreen rendering with multisampling for antialiasing.
    this.colorFBO = getFBO(1, 1, { samples: 4 });

    // Shader material for color effects, using the orthographic vertex shader and custom fragment shader.
    this.colorShader = new RawShaderMaterial({
      uniforms: {
        inputTexture: { value: this.colorFBO.texture }, // Texture from FBO.
        time: { value: 0 }, // Time uniform for animated effects.
      },
      vertexShader: orthoVertexShader, // Vertex shader for 2D screen space.
      fragmentShader: colorFragmentShader, // Fragment shader for color effects.
      glslVersion: GLSL3, // Specify GLSL version.
    });

    // Shader pass for applying color effects to the rendered scene.
    this.colorPass = new ShaderPass(this.colorShader, {
      format: RGBAFormat, // Texture format.
      type: UnsignedByteType, // Texture type.
      minFilter: LinearFilter, // Minification filter.
      magFilter: LinearFilter, // Magnification filter.
      wrapS: ClampToEdgeWrapping, // S-axis wrapping.
      wrapT: ClampToEdgeWrapping, // T-axis wrapping.
    });

    // Final shader material for combining the scene with bloom and other effects.
    this.finalShader = new RawShaderMaterial({
      uniforms: {
        resolution: { value: new Vector2(1, 1) }, // Screen resolution.
        vignetteBoost: { value: params.vignetteBoost || 1.1 }, // Vignette boost factor.
        vignetteReduction: { value: params.vignetteReduction || 0.8 }, // Vignette reduction factor.
        inputTexture: { value: this.colorPass.texture }, // Texture from color pass.
        blur0Texture: { value: null }, // Blur textures to be set during rendering.
        blur1Texture: { value: null },
        blur2Texture: { value: null },
        blur3Texture: { value: null },
        blur4Texture: { value: null },
        time: { value: 0 }, // Time uniform.
      },
      vertexShader: orthoVertexShader, // 2D screen space vertex shader.
      fragmentShader: finalFragmentShader, // Fragment shader for final effects.
      glslVersion: GLSL3, // GLSL version.
    });
    // Shader pass for the final rendering stage, applying all effects.
    this.finalPass = new ShaderPass(this.finalShader, {
      format: RGBAFormat,
      type: UnsignedByteType,
      minFilter: LinearFilter,
      magFilter: LinearFilter,
      wrapS: ClampToEdgeWrapping,
      wrapT: ClampToEdgeWrapping,
    });

    // Bloom pass for creating bloom effects based on bright areas of the scene.
    this.bloomPass = new BloomPass(5, 5); // Initializes with specific blur strength and resolution.
  }

  // Function to update the size of all render targets and shaders based on the new dimensions.
  setSize(w, h) {
    this.colorFBO.setSize(w, h); // Update color FBO size.
    this.colorPass.setSize(w, h); // Update color pass size.
    this.finalPass.setSize(w, h); // Update final pass size.
    this.finalShader.uniforms.resolution.value.set(w, h); // Update resolution uniform in final shader.
    this.bloomPass.setSize(w, h); // Update bloom pass size.
  }

  // The render function encapsulates the entire post-processing pipeline.
  render(scene, camera) {
    const t = Math.random() * 100000; // Generate a random time value for animated effects.
    this.colorPass.shader.uniforms.time.value = t; // Set time uniform for color pass.
    this.renderer.setRenderTarget(this.colorFBO); // Set the render target to FBO for offscreen rendering.
    this.renderer.render(scene, camera, this.colorFBO); // Render the scene into the FBO.
    this.renderer.setRenderTarget(null); // Reset render target to default (screen).

    // Update the input texture for the color pass to the latest rendered texture.
    this.colorPass.shader.uniforms.inputTexture.value = this.colorFBO.texture;
    this.colorPass.render(this.renderer); // Execute the color pass.

    // Set the source texture for the bloom pass to the result of the color pass.
    this.bloomPass.source = this.colorPass.texture;
    this.bloomPass.render(this.renderer); // Execute the bloom pass.

    // Update the blur textures in the final shader with the textures from the bloom pass.
    this.finalPass.shader.uniforms.blur0Texture.value = this.bloomPass.blurPasses[0].texture;
    this.finalPass.shader.uniforms.blur1Texture.value = this.bloomPass.blurPasses[1].texture;
    this.finalPass.shader.uniforms.blur2Texture.value = this.bloomPass.blurPasses[2].texture;
    this.finalPass.shader.uniforms.blur3Texture.value = this.bloomPass.blurPasses[3].texture;
    this.finalPass.shader.uniforms.blur4Texture.value = this.bloomPass.blurPasses[4].texture;
    this.finalPass.shader.uniforms.time.value = t; // Update time uniform for final pass.

    this.finalPass.render(this.renderer, true); // Execute the final pass, rendering the result to the screen.
  }
}

// Export the Post class for use in other modules.
export { Post };
