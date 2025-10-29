import { useState, useEffect } from 'react';
import './CodeRenderer.css';
import * as React from 'react';

// Error boundary component to catch runtime errors
class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }

  componentDidCatch(error, errorInfo) {
    console.error('Component runtime error:', error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="code-renderer-error">
          <div className="error-title">[RUNTIME ERROR] Component crashed</div>
          <div className="error-message">{this.state.error?.message || 'Unknown error'}</div>
          <div className="error-hint">The agent's code tried to access restricted browser APIs (like CSS rules). Try giving feedback to improve the code.</div>
        </div>
      );
    }

    return this.props.children;
  }
}

function CodeRenderer({ code, onClose }) {
  const [RenderedComponent, setRenderedComponent] = useState(null);
  const [error, setError] = useState(null);
  const [isTransforming, setIsTransforming] = useState(false);

  useEffect(() => {
    // Check if code is empty or invalid
    if (!code || typeof code !== 'string' || code.trim().length === 0) {
      console.log('Code is empty or invalid:', code);
      setRenderedComponent(null);
      setError(null);
      return;
    }

    setIsTransforming(true);

    const loadBabelAndTransform = async () => {
      try {
        console.log('=== CodeRenderer Debug ===');
        console.log('Original code received (first 300 chars):', code.substring(0, 300));

        // Dynamically import Babel
        const Babel = await import('@babel/standalone');

        // Strip markdown code fences if present
        let cleanCode = code.trim();

        // Remove markdown code fences (```jsx, ```javascript, ```js, etc.)
        cleanCode = cleanCode.replace(/^```[\w]*\n?/gm, '').replace(/```$/gm, '');

        // Remove import statements and export keywords
        cleanCode = cleanCode
          .replace(/import\s+.*?from\s+['"].*?['"];?\n?/g, '')
          .replace(/export\s+(default\s+)?/g, '');

        // Trim whitespace
        cleanCode = cleanCode.trim();

        console.log('Cleaned code (first 300 chars):', cleanCode.substring(0, 300));

        // Transform JSX to regular JavaScript using Babel FIRST
        const transformed = Babel.transform(cleanCode, {
          presets: ['react'],
          filename: 'component.jsx'
        }).code;

        console.log('Transformed code (FULL):', transformed);

        // Find the component name in the TRANSFORMED code
        let componentMatch = transformed.match(/(?:function|const|let|var)\s+(\w+)/);

        console.log('Component match result:', componentMatch);

        if (!componentMatch || !componentMatch[1]) {
          console.error('Failed to extract component name!');
          console.error('Transformed code:', transformed);
          throw new Error('Could not find component name. The AI might have generated invalid code or comments only.');
        }

        const componentName = componentMatch[1];
        console.log('Found component name:', componentName);

        if (!componentName || componentName.trim() === '') {
          throw new Error('Component name is empty!');
        }

        // Check if it's actually defined in the code
        if (!transformed.includes(componentName)) {
          throw new Error(`Component name ${componentName} not found in transformed code`);
        }

        // Create executable code that defines the component and returns it
        const executableCode = `
          ${transformed}

          if (typeof ${componentName} === 'undefined') {
            throw new Error('Component ${componentName} is undefined after execution');
          }

          return ${componentName};
        `;

        console.log('Executable code:', executableCode);

        // Execute the code with React and hooks available
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

        console.log('Component extracted:', Component);
        console.log('Component type:', typeof Component);

        if (typeof Component !== 'function') {
          throw new Error(`Component "${componentName}" is not a function. Got: ${typeof Component}`);
        }

        setRenderedComponent(() => Component);
        setError(null);
        setIsTransforming(false);
      } catch (err) {
        console.error('Failed to render code:', err);
        console.error('Error stack:', err.stack);
        setError(err.message);
        setIsTransforming(false);
      }
    };

    loadBabelAndTransform();
  }, [code]);

  return (
    <div className="code-renderer-inline">
      <div className="code-renderer-content">
        {error ? (
          <div className="code-renderer-error">
            <div className="error-title">[ERROR] Failed to render component</div>
            <div className="error-message">{error}</div>
          </div>
        ) : RenderedComponent ? (
          <ErrorBoundary>
            <div className="rendered-component-wrapper">
              <RenderedComponent />
            </div>
          </ErrorBoundary>
        ) : isTransforming ? (
          <div className="code-renderer-loading">transforming code...</div>
        ) : (
          <div className="code-renderer-empty">waiting for code...</div>
        )}
      </div>
    </div>
  );
}

export default CodeRenderer;
