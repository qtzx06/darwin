import { useState, useEffect } from 'react';
import './CodeRenderer.css';
import * as React from 'react';

function CodeRenderer({ code, onClose }) {
  const [RenderedComponent, setRenderedComponent] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (!code) return;

    const loadBabelAndTransform = async () => {
      try {
        // Dynamically import Babel
        const Babel = await import('@babel/standalone');

        // Remove import statements and export keywords
        let cleanCode = code
          .replace(/import\s+.*?from\s+['"].*?['"];?\n?/g, '')
          .replace(/export\s+(default\s+)?/g, '');

        // Transform JSX to regular JavaScript using Babel
        const transformed = Babel.transform(cleanCode, {
          presets: ['react'],
          filename: 'component.tsx'
        }).code;

        // Find the component name
        const componentMatch = cleanCode.match(/(?:function|const)\s+(\w+)/);
        const componentName = componentMatch ? componentMatch[1] : 'Component';

        // Wrap in IIFE and return the component
        const executableCode = `
          ${transformed}
          return ${componentName};
        `;

        console.log('Transformed code:', transformed);

        // Execute the code with React hooks available
        const Component = new Function(
          'React',
          'useState',
          'useEffect',
          'useRef',
          'useMemo',
          'useCallback',
          executableCode
        )(
          React,
          React.useState,
          React.useEffect,
          React.useRef,
          React.useMemo,
          React.useCallback
        );

        setRenderedComponent(() => Component);
        setError(null);
      } catch (err) {
        console.error('Failed to render code:', err);
        setError(err.message);
      }
    };

    loadBabelAndTransform();
  }, [code]);

  if (!code) return null;

  return (
    <div className="code-renderer-inline">
      <div className="code-renderer-content">
        {error ? (
          <div className="code-renderer-error">
            <div className="error-title">[ERROR] Failed to render component</div>
            <div className="error-message">{error}</div>
          </div>
        ) : RenderedComponent ? (
          <div className="rendered-component-wrapper">
            <RenderedComponent />
          </div>
        ) : (
          <div className="code-renderer-loading">Loading component...</div>
        )}
      </div>
    </div>
  );
}

export default CodeRenderer;
