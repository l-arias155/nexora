import {
  IsOptional,
  IsString,
  Matches,
  MaxLength,
  MinLength,
} from 'class-validator';

export class CreateOrganizationDto {
  @IsString()
  @MinLength(2)
  @MaxLength(120)
  name!: string;

  /** Opcional: si no se provee, se deriva de `name`. */
  @IsOptional()
  @IsString()
  @Matches(/^[a-z0-9]+(-[a-z0-9]+)*$/, {
    message:
      'El slug solo puede contener minúsculas, números y guiones simples.',
  })
  @MinLength(2)
  @MaxLength(60)
  slug?: string;
}
