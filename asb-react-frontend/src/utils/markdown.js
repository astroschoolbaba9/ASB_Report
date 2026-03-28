import React from 'react';

/**
 * Shared utility to render structured AI interpretations.
 * Supports: Headers (###, ####), Bold (**), and Bullet Points (-).
 */
export const formatInterpretation = (text) => {
    if (!text) return null;

    // Safety check: ensure text is a string
    if (typeof text !== 'string') {
        text = text.interpretation || text.summary || JSON.stringify(text);
        if (typeof text !== 'string') return null;
    }

    // Split by double newline for paragraphs/sections
    const sections = text.split('\n\n');

    return sections.map((section, idx) => {
        // Headers
        if (section.startsWith('### ')) {
            return (
                <h3 key={idx} className="text-xl font-bold font-playfair text-asb-violet mt-6 mb-4 flex items-center gap-2">
                    {parseInline(section.replace('### ', ''))}
                </h3>
            );
        }
        if (section.startsWith('#### ')) {
            return (
                <h4 key={idx} className="text-lg font-semibold font-playfair text-gray-800 mt-4 mb-2">
                    {parseInline(section.replace('#### ', ''))}
                </h4>
            );
        }

        // Lists
        if (section.includes('\n- ')) {
            const lines = section.split('\n');
            const intro = lines[0].startsWith('- ') ? '' : lines[0];
            const items = lines.filter(l => l.startsWith('- ')).map(l => l.replace('- ', ''));

            return (
                <div key={idx} className="mb-4">
                    {intro && <p className="mb-2 font-medium text-gray-800">{parseInline(intro)}</p>}
                    <ul className="space-y-2 ml-4">
                        {items.map((item, i) => (
                            <li key={i} className="flex gap-2 text-gray-700">
                                <span className="text-asb-magenta">•</span>
                                <span>{parseInline(item)}</span>
                            </li>
                        ))}
                    </ul>
                </div>
            );
        }

        // Regular Paragraph
        return (
            <p key={idx} className="mb-4 text-gray-700 leading-relaxed font-light">
                {parseInline(section)}
            </p>
        );
    });
};

/**
 * Parses inline markers like **bold** and *italic*
 */
export const parseInline = (text) => {
    if (!text) return '';

    // Simple regex for bold
    const parts = text.split(/(\*\*.*?\*\*)/g);
    return parts.map((part, i) => {
        if (part.startsWith('**') && part.endsWith('**')) {
            return <strong key={i} className="font-bold text-gray-900">{part.slice(2, -2)}</strong>;
        }
        return part;
    });
};
