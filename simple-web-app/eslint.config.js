export default [
    {
        files: ['src/**/*.js'],
        ignores: ['dist/**/*', 'node_modules/**/*'],
        languageOptions: {
            ecmaVersion: 2021,
            sourceType: 'module',
            globals: {
                window: 'readonly',
                document: 'readonly',
                console: 'readonly',
                alert: 'readonly',
                module: 'readonly',
                exports: 'readonly'
            }
        },
        rules: {
            'semi': ['error', 'always'],
            'quotes': ['error', 'single'],
            'no-unused-vars': 'warn',
            'no-console': 'off',
            'indent': ['error', 4],
            'no-trailing-spaces': 'error',
            'eol-last': 'error',
            'no-multiple-empty-lines': ['error', { 'max': 2 }]
        }
    }
]; 